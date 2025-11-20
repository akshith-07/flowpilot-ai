"""
Analytics models for FlowPilot AI.
Handles metrics, reporting, and dashboards.
"""
import uuid
from django.db import models
from apps.organizations.models import Organization


class DailyMetrics(models.Model):
    """Aggregated daily metrics for organizations."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='daily_metrics')
    date = models.DateField(db_index=True)

    # Workflow metrics
    workflows_created = models.IntegerField(default=0)
    workflows_executed = models.IntegerField(default=0)
    workflows_failed = models.IntegerField(default=0)

    # Execution metrics
    total_executions = models.IntegerField(default=0)
    successful_executions = models.IntegerField(default=0)
    failed_executions = models.IntegerField(default=0)
    avg_execution_duration = models.FloatField(default=0)

    # AI metrics
    ai_requests_count = models.IntegerField(default=0)
    total_ai_tokens = models.BigIntegerField(default=0)
    total_ai_cost = models.DecimalField(max_digits=10, decimal_places=4, default=0)

    # Document metrics
    documents_processed = models.IntegerField(default=0)
    documents_size_bytes = models.BigIntegerField(default=0)

    # User activity
    active_users = models.IntegerField(default=0)
    api_calls = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'daily_metrics'
        unique_together = [['organization', 'date']]
        ordering = ['-date']
        indexes = [
            models.Index(fields=['organization', '-date']),
        ]

    def __str__(self):
        return f'{self.organization.name} - {self.date}'


class UserActivity(models.Model):
    """Track user activity for analytics."""

    ACTION_CHOICES = [
        ('login', 'Login'),
        ('workflow_create', 'Workflow Create'),
        ('workflow_execute', 'Workflow Execute'),
        ('document_upload', 'Document Upload'),
        ('api_call', 'API Call'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='user_activities')
    user_email = models.EmailField()
    action = models.CharField(max_length=50, choices=ACTION_CHOICES, db_index=True)
    resource_type = models.CharField(max_length=50, null=True, blank=True)
    resource_id = models.CharField(max_length=255, null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = 'user_activities'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['organization', '-created_at']),
            models.Index(fields=['action', '-created_at']),
        ]


class ErrorLog(models.Model):
    """Track errors for monitoring."""

    SEVERITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='error_logs', null=True, blank=True)
    error_type = models.CharField(max_length=100)
    error_message = models.TextField()
    stack_trace = models.TextField(null=True, blank=True)
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, default='medium')
    context = models.JSONField(default=dict, blank=True)
    count = models.IntegerField(default=1)  # For grouping duplicate errors
    first_seen = models.DateTimeField(auto_now_add=True)
    last_seen = models.DateTimeField(auto_now=True)
    is_resolved = models.BooleanField(default=False)

    class Meta:
        db_table = 'error_logs'
        ordering = ['-last_seen']
        indexes = [
            models.Index(fields=['organization', '-last_seen']),
            models.Index(fields=['severity', '-last_seen']),
        ]
