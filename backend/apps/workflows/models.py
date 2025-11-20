"""
Workflow models for FlowPilot AI.
Includes Workflow, WorkflowVersion, WorkflowTemplate, WorkflowVariable, and WorkflowTrigger.
"""
import uuid
from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.organizations.models import Organization

User = get_user_model()


class WorkflowTemplate(models.Model):
    """
    Pre-built workflow templates.
    """
    CATEGORY_CHOICES = [
        ('email', 'Email Automation'),
        ('data', 'Data Processing'),
        ('document', 'Document Processing'),
        ('integration', 'Integration'),
        ('ai', 'AI Processing'),
        ('notification', 'Notification'),
        ('other', 'Other'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, db_index=True)
    slug = models.SlugField(max_length=255, unique=True, db_index=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='other')

    # Template details
    description = models.TextField()
    thumbnail_url = models.URLField(max_length=500, null=True, blank=True)
    tags = models.JSONField(default=list, blank=True)

    # Template definition (JSONB)
    definition = models.JSONField(default=dict)

    # Metadata
    is_public = models.BooleanField(default=True, db_index=True)
    is_featured = models.BooleanField(default=False, db_index=True)
    use_count = models.IntegerField(default=0, validators=[MinValueValidator(0)])

    # Author
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_templates'
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'workflow_templates'
        verbose_name = 'Workflow Template'
        verbose_name_plural = 'Workflow Templates'
        ordering = ['-is_featured', '-use_count', '-created_at']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['category', '-created_at']),
            models.Index(fields=['-use_count']),
        ]

    def __str__(self):
        return self.name

    def increment_use_count(self):
        """Increment template use count."""
        self.use_count += 1
        self.save(update_fields=['use_count'])


class Workflow(models.Model):
    """
    Main workflow model with JSONB definition.
    """
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('archived', 'Archived'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='workflows'
    )
    name = models.CharField(max_length=255, db_index=True)
    description = models.TextField(null=True, blank=True)

    # Workflow definition (JSONB - contains nodes, edges, etc.)
    definition = models.JSONField(default=dict)

    # Status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
        db_index=True
    )
    is_active = models.BooleanField(default=False, db_index=True)

    # Versioning
    version = models.IntegerField(default=1, validators=[MinValueValidator(1)])
    current_version = models.ForeignKey(
        'WorkflowVersion',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='+'
    )

    # Template reference
    template = models.ForeignKey(
        WorkflowTemplate,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='workflows'
    )

    # Owner
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_workflows'
    )
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='updated_workflows'
    )

    # Metadata
    tags = models.JSONField(default=list, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    # Statistics
    execution_count = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    success_count = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    failure_count = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    last_executed_at = models.DateTimeField(null=True, blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'workflows'
        verbose_name = 'Workflow'
        verbose_name_plural = 'Workflows'
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['organization', 'status']),
            models.Index(fields=['organization', 'is_active']),
            models.Index(fields=['created_by']),
            models.Index(fields=['-updated_at']),
        ]

    def __str__(self):
        return f'{self.name} (v{self.version})'

    @property
    def success_rate(self):
        """Calculate success rate percentage."""
        if self.execution_count == 0:
            return 0
        return (self.success_count / self.execution_count) * 100

    def create_version(self, definition=None, created_by=None):
        """
        Create a new version of the workflow.

        Args:
            definition: New workflow definition (defaults to current)
            created_by: User creating the version

        Returns:
            WorkflowVersion: New version instance
        """
        if definition is None:
            definition = self.definition

        version = WorkflowVersion.objects.create(
            workflow=self,
            version_number=self.version + 1,
            definition=definition,
            created_by=created_by
        )

        self.version = version.version_number
        self.current_version = version
        self.save(update_fields=['version', 'current_version', 'updated_at'])

        return version

    def rollback_to_version(self, version_number):
        """
        Rollback workflow to a specific version.

        Args:
            version_number: Version number to rollback to

        Returns:
            WorkflowVersion: Version instance
        """
        version = self.versions.get(version_number=version_number)
        self.definition = version.definition
        self.current_version = version
        self.save(update_fields=['definition', 'current_version', 'updated_at'])

        return version


class WorkflowVersion(models.Model):
    """
    Workflow version control.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workflow = models.ForeignKey(
        Workflow,
        on_delete=models.CASCADE,
        related_name='versions'
    )
    version_number = models.IntegerField(validators=[MinValueValidator(1)])

    # Version definition
    definition = models.JSONField(default=dict)

    # Metadata
    change_summary = models.TextField(null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    # Author
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='workflow_versions'
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = 'workflow_versions'
        verbose_name = 'Workflow Version'
        verbose_name_plural = 'Workflow Versions'
        ordering = ['-version_number']
        constraints = [
            models.UniqueConstraint(
                fields=['workflow', 'version_number'],
                name='unique_version_per_workflow'
            )
        ]
        indexes = [
            models.Index(fields=['workflow', '-version_number']),
        ]

    def __str__(self):
        return f'{self.workflow.name} - v{self.version_number}'


class WorkflowVariable(models.Model):
    """
    Workflow variables for dynamic data.
    """
    VARIABLE_TYPE_CHOICES = [
        ('string', 'String'),
        ('number', 'Number'),
        ('boolean', 'Boolean'),
        ('array', 'Array'),
        ('object', 'Object'),
    ]

    SCOPE_CHOICES = [
        ('global', 'Global'),
        ('local', 'Local'),
        ('environment', 'Environment'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workflow = models.ForeignKey(
        Workflow,
        on_delete=models.CASCADE,
        related_name='variables'
    )
    name = models.CharField(max_length=100, db_index=True)
    variable_type = models.CharField(
        max_length=20,
        choices=VARIABLE_TYPE_CHOICES,
        default='string'
    )
    scope = models.CharField(
        max_length=20,
        choices=SCOPE_CHOICES,
        default='local'
    )

    # Value
    default_value = models.JSONField(null=True, blank=True)
    is_required = models.BooleanField(default=False)
    is_secret = models.BooleanField(default=False)

    # Description
    description = models.TextField(null=True, blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'workflow_variables'
        verbose_name = 'Workflow Variable'
        verbose_name_plural = 'Workflow Variables'
        ordering = ['workflow', 'name']
        constraints = [
            models.UniqueConstraint(
                fields=['workflow', 'name'],
                name='unique_variable_per_workflow'
            )
        ]
        indexes = [
            models.Index(fields=['workflow']),
        ]

    def __str__(self):
        return f'{self.workflow.name} - {self.name}'


class WorkflowTrigger(models.Model):
    """
    Workflow triggers for automated execution.
    """
    TRIGGER_TYPE_CHOICES = [
        ('manual', 'Manual'),
        ('scheduled', 'Scheduled (Cron)'),
        ('webhook', 'Webhook'),
        ('event', 'Event-Driven'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workflow = models.ForeignKey(
        Workflow,
        on_delete=models.CASCADE,
        related_name='triggers'
    )
    name = models.CharField(max_length=255)
    trigger_type = models.CharField(
        max_length=20,
        choices=TRIGGER_TYPE_CHOICES,
        default='manual',
        db_index=True
    )

    # Trigger configuration
    config = models.JSONField(default=dict, blank=True)

    # For scheduled triggers
    cron_expression = models.CharField(max_length=100, null=True, blank=True)
    timezone = models.CharField(max_length=50, default='UTC')

    # For webhook triggers
    webhook_url = models.CharField(max_length=500, null=True, blank=True, unique=True)
    webhook_secret = models.CharField(max_length=255, null=True, blank=True)

    # Status
    is_active = models.BooleanField(default=True, db_index=True)

    # Statistics
    execution_count = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    last_triggered_at = models.DateTimeField(null=True, blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'workflow_triggers'
        verbose_name = 'Workflow Trigger'
        verbose_name_plural = 'Workflow Triggers'
        ordering = ['workflow', '-created_at']
        indexes = [
            models.Index(fields=['workflow', 'is_active']),
            models.Index(fields=['trigger_type']),
        ]

    def __str__(self):
        return f'{self.workflow.name} - {self.name} ({self.trigger_type})'

    def increment_execution_count(self):
        """Increment trigger execution count."""
        self.execution_count += 1
        self.last_triggered_at = timezone.now()
        self.save(update_fields=['execution_count', 'last_triggered_at', 'updated_at'])
