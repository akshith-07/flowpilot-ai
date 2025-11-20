"""
Execution models for FlowPilot AI.
Includes WorkflowExecution, ExecutionStep, ExecutionLog, and AIRequest.
"""
import uuid
from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from apps.workflows.models import Workflow, WorkflowTrigger

User = get_user_model()


class WorkflowExecution(models.Model):
    """
    Main workflow execution model with state machine.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
        ('paused', 'Paused'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workflow = models.ForeignKey(
        Workflow,
        on_delete=models.CASCADE,
        related_name='executions'
    )

    # Execution details
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        db_index=True
    )

    # Input/Output
    input_data = models.JSONField(default=dict, blank=True)
    output_data = models.JSONField(default=dict, blank=True)
    error_message = models.TextField(null=True, blank=True)
    error_details = models.JSONField(default=dict, blank=True)

    # Execution context
    context = models.JSONField(default=dict, blank=True)  # Execution variables and state

    # Trigger information
    trigger = models.ForeignKey(
        WorkflowTrigger,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='executions'
    )
    triggered_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='triggered_executions'
    )

    # Execution metrics
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    duration = models.FloatField(null=True, blank=True)  # Duration in seconds

    # Resource usage
    memory_usage = models.BigIntegerField(null=True, blank=True)  # In bytes
    cpu_time = models.FloatField(null=True, blank=True)  # In seconds
    ai_tokens_used = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    ai_cost = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        default=0,
        validators=[MinValueValidator(0)]
    )

    # Retry information
    retry_count = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    max_retries = models.IntegerField(default=3, validators=[MinValueValidator(0)])
    parent_execution = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='retry_executions'
    )

    # Metadata
    metadata = models.JSONField(default=dict, blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'workflow_executions'
        verbose_name = 'Workflow Execution'
        verbose_name_plural = 'Workflow Executions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['workflow', 'status']),
            models.Index(fields=['workflow', '-created_at']),
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['triggered_by']),
        ]

    def __str__(self):
        return f'{self.workflow.name} - {self.status} - {self.created_at}'

    def start(self):
        """Mark execution as started."""
        self.status = 'running'
        self.started_at = timezone.now()
        self.save(update_fields=['status', 'started_at', 'updated_at'])

    def complete(self, output_data=None):
        """
        Mark execution as completed.

        Args:
            output_data: Final output data
        """
        self.status = 'completed'
        self.completed_at = timezone.now()

        if output_data:
            self.output_data = output_data

        # Calculate duration
        if self.started_at:
            self.duration = (self.completed_at - self.started_at).total_seconds()

        self.save(update_fields=[
            'status', 'completed_at', 'output_data', 'duration', 'updated_at'
        ])

        # Update workflow statistics
        self.workflow.success_count += 1
        self.workflow.execution_count += 1
        self.workflow.last_executed_at = self.completed_at
        self.workflow.save(update_fields=[
            'success_count', 'execution_count', 'last_executed_at', 'updated_at'
        ])

    def fail(self, error_message, error_details=None):
        """
        Mark execution as failed.

        Args:
            error_message: Error message
            error_details: Additional error details
        """
        self.status = 'failed'
        self.completed_at = timezone.now()
        self.error_message = error_message

        if error_details:
            self.error_details = error_details

        # Calculate duration
        if self.started_at:
            self.duration = (self.completed_at - self.started_at).total_seconds()

        self.save(update_fields=[
            'status', 'completed_at', 'error_message', 'error_details',
            'duration', 'updated_at'
        ])

        # Update workflow statistics
        self.workflow.failure_count += 1
        self.workflow.execution_count += 1
        self.workflow.last_executed_at = self.completed_at
        self.workflow.save(update_fields=[
            'failure_count', 'execution_count', 'last_executed_at', 'updated_at'
        ])

    def cancel(self):
        """Cancel execution."""
        self.status = 'cancelled'
        self.completed_at = timezone.now()

        # Calculate duration
        if self.started_at:
            self.duration = (self.completed_at - self.started_at).total_seconds()

        self.save(update_fields=['status', 'completed_at', 'duration', 'updated_at'])

    def pause(self):
        """Pause execution."""
        self.status = 'paused'
        self.save(update_fields=['status', 'updated_at'])

    def resume(self):
        """Resume execution."""
        self.status = 'running'
        self.save(update_fields=['status', 'updated_at'])

    def can_retry(self):
        """Check if execution can be retried."""
        return self.status == 'failed' and self.retry_count < self.max_retries

    def create_retry(self, triggered_by=None):
        """
        Create a retry execution.

        Args:
            triggered_by: User triggering the retry

        Returns:
            WorkflowExecution: New retry execution
        """
        retry_execution = WorkflowExecution.objects.create(
            workflow=self.workflow,
            input_data=self.input_data,
            context=self.context,
            trigger=self.trigger,
            triggered_by=triggered_by or self.triggered_by,
            retry_count=self.retry_count + 1,
            max_retries=self.max_retries,
            parent_execution=self,
            metadata=self.metadata
        )

        return retry_execution


class ExecutionStep(models.Model):
    """
    Individual step execution tracking.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('skipped', 'Skipped'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    execution = models.ForeignKey(
        WorkflowExecution,
        on_delete=models.CASCADE,
        related_name='steps'
    )

    # Step details
    node_id = models.CharField(max_length=255, db_index=True)
    node_type = models.CharField(max_length=100)
    node_name = models.CharField(max_length=255, null=True, blank=True)
    step_number = models.IntegerField(validators=[MinValueValidator(1)])

    # Status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        db_index=True
    )

    # Input/Output
    input_data = models.JSONField(default=dict, blank=True)
    output_data = models.JSONField(default=dict, blank=True)
    error_message = models.TextField(null=True, blank=True)
    error_details = models.JSONField(default=dict, blank=True)

    # Execution metrics
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    duration = models.FloatField(null=True, blank=True)  # Duration in seconds

    # Retry information
    retry_count = models.IntegerField(default=0, validators=[MinValueValidator(0)])

    # Metadata
    metadata = models.JSONField(default=dict, blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'execution_steps'
        verbose_name = 'Execution Step'
        verbose_name_plural = 'Execution Steps'
        ordering = ['execution', 'step_number']
        indexes = [
            models.Index(fields=['execution', 'step_number']),
            models.Index(fields=['execution', 'status']),
            models.Index(fields=['node_id']),
        ]

    def __str__(self):
        return f'{self.execution.id} - Step {self.step_number} - {self.node_name or self.node_id}'

    def start(self):
        """Mark step as started."""
        self.status = 'running'
        self.started_at = timezone.now()
        self.save(update_fields=['status', 'started_at', 'updated_at'])

    def complete(self, output_data=None):
        """
        Mark step as completed.

        Args:
            output_data: Step output data
        """
        self.status = 'completed'
        self.completed_at = timezone.now()

        if output_data:
            self.output_data = output_data

        # Calculate duration
        if self.started_at:
            self.duration = (self.completed_at - self.started_at).total_seconds()

        self.save(update_fields=[
            'status', 'completed_at', 'output_data', 'duration', 'updated_at'
        ])

    def fail(self, error_message, error_details=None):
        """
        Mark step as failed.

        Args:
            error_message: Error message
            error_details: Additional error details
        """
        self.status = 'failed'
        self.completed_at = timezone.now()
        self.error_message = error_message

        if error_details:
            self.error_details = error_details

        # Calculate duration
        if self.started_at:
            self.duration = (self.completed_at - self.started_at).total_seconds()

        self.save(update_fields=[
            'status', 'completed_at', 'error_message', 'error_details',
            'duration', 'updated_at'
        ])

    def skip(self):
        """Mark step as skipped."""
        self.status = 'skipped'
        self.completed_at = timezone.now()
        self.save(update_fields=['status', 'completed_at', 'updated_at'])


class ExecutionLog(models.Model):
    """
    Execution logs for debugging and monitoring.
    """
    LEVEL_CHOICES = [
        ('debug', 'Debug'),
        ('info', 'Info'),
        ('warning', 'Warning'),
        ('error', 'Error'),
        ('critical', 'Critical'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    execution = models.ForeignKey(
        WorkflowExecution,
        on_delete=models.CASCADE,
        related_name='logs'
    )
    step = models.ForeignKey(
        ExecutionStep,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='logs'
    )

    # Log details
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default='info', db_index=True)
    message = models.TextField()
    details = models.JSONField(default=dict, blank=True)

    # Timestamp
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = 'execution_logs'
        verbose_name = 'Execution Log'
        verbose_name_plural = 'Execution Logs'
        ordering = ['execution', 'created_at']
        indexes = [
            models.Index(fields=['execution', 'created_at']),
            models.Index(fields=['execution', 'level']),
            models.Index(fields=['step', 'created_at']),
        ]

    def __str__(self):
        return f'{self.execution.id} - {self.level} - {self.message[:50]}'


class AIRequest(models.Model):
    """
    Track AI API requests for monitoring and cost calculation.
    """
    PROVIDER_CHOICES = [
        ('gemini', 'Google Gemini'),
        ('openai', 'OpenAI'),
        ('anthropic', 'Anthropic'),
        ('other', 'Other'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    execution = models.ForeignKey(
        WorkflowExecution,
        on_delete=models.CASCADE,
        related_name='ai_requests'
    )
    step = models.ForeignKey(
        ExecutionStep,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='ai_requests'
    )

    # AI provider details
    provider = models.CharField(max_length=50, choices=PROVIDER_CHOICES, default='gemini')
    model = models.CharField(max_length=100)

    # Request/Response
    prompt = models.TextField()
    response = models.TextField(null=True, blank=True)
    system_prompt = models.TextField(null=True, blank=True)

    # Token usage
    input_tokens = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    output_tokens = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    total_tokens = models.IntegerField(default=0, validators=[MinValueValidator(0)])

    # Cost
    cost = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        default=0,
        validators=[MinValueValidator(0)]
    )

    # Performance metrics
    duration = models.FloatField(null=True, blank=True)  # Duration in seconds

    # Status
    success = models.BooleanField(default=True)
    error_message = models.TextField(null=True, blank=True)

    # Metadata
    metadata = models.JSONField(default=dict, blank=True)

    # Timestamp
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = 'ai_requests'
        verbose_name = 'AI Request'
        verbose_name_plural = 'AI Requests'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['execution', '-created_at']),
            models.Index(fields=['step', '-created_at']),
            models.Index(fields=['provider', '-created_at']),
        ]

    def __str__(self):
        return f'{self.provider} - {self.model} - {self.total_tokens} tokens'

    def save(self, *args, **kwargs):
        """Calculate total tokens on save."""
        self.total_tokens = self.input_tokens + self.output_tokens
        super().save(*args, **kwargs)
