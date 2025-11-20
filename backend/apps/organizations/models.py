"""
Organization models for FlowPilot AI.
Includes Organization, OrganizationMember, Role, Invitation, Department, and UsageQuota.
"""
import uuid
from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator

User = get_user_model()


class Organization(models.Model):
    """
    Organization model for multi-tenancy.
    Supports hierarchical structure with parent-child relationships.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, db_index=True)
    slug = models.SlugField(max_length=255, unique=True, db_index=True)

    # Hierarchy
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children'
    )

    # Organization details
    description = models.TextField(null=True, blank=True)
    website = models.URLField(max_length=500, null=True, blank=True)
    logo_url = models.URLField(max_length=500, null=True, blank=True)

    # Contact information
    email = models.EmailField(max_length=255, null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)

    # Address
    address_line1 = models.CharField(max_length=255, null=True, blank=True)
    address_line2 = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=100, null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    postal_code = models.CharField(max_length=20, null=True, blank=True)

    # Settings (JSONB for flexible configuration)
    settings = models.JSONField(default=dict, blank=True)

    # Metadata
    metadata = models.JSONField(default=dict, blank=True)

    # Status
    is_active = models.BooleanField(default=True, db_index=True)

    # Branding
    primary_color = models.CharField(max_length=7, default='#3B82F6')  # Hex color
    timezone = models.CharField(max_length=50, default='UTC')
    locale = models.CharField(max_length=10, default='en')

    # Owner
    owner = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='owned_organizations'
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'organizations'
        verbose_name = 'Organization'
        verbose_name_plural = 'Organizations'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['is_active', '-created_at']),
            models.Index(fields=['owner']),
        ]

    def __str__(self):
        return self.name

    @property
    def member_count(self):
        """Get total number of active members."""
        return self.members.filter(is_active=True).count()

    @property
    def workflow_count(self):
        """Get total number of workflows."""
        return self.workflows.count()

    def get_all_members(self):
        """Get all active organization members."""
        return self.members.filter(is_active=True).select_related('user', 'role')


class Role(models.Model):
    """
    Role model for organization-level permissions.
    """
    ROLE_TYPE_CHOICES = [
        ('owner', 'Owner'),
        ('admin', 'Administrator'),
        ('manager', 'Manager'),
        ('member', 'Member'),
        ('viewer', 'Viewer'),
        ('custom', 'Custom Role'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='roles'
    )
    name = models.CharField(max_length=100)
    role_type = models.CharField(max_length=20, choices=ROLE_TYPE_CHOICES, default='custom')
    description = models.TextField(null=True, blank=True)

    # Permissions matrix (JSONB for flexible permissions)
    permissions = models.JSONField(default=dict, blank=True)

    # Status
    is_active = models.BooleanField(default=True, db_index=True)
    is_system_role = models.BooleanField(default=False)  # System roles cannot be deleted

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'roles'
        verbose_name = 'Role'
        verbose_name_plural = 'Roles'
        ordering = ['organization', 'name']
        constraints = [
            models.UniqueConstraint(
                fields=['organization', 'name'],
                name='unique_role_per_organization'
            )
        ]
        indexes = [
            models.Index(fields=['organization', 'role_type']),
        ]

    def __str__(self):
        return f'{self.organization.name} - {self.name}'

    def has_permission(self, module, action):
        """
        Check if role has specific permission.

        Args:
            module: Module name (e.g., 'workflows', 'documents')
            action: Action name (e.g., 'create', 'read', 'update', 'delete')

        Returns:
            bool: True if role has permission
        """
        if not self.permissions:
            return False

        module_permissions = self.permissions.get(module, {})
        return module_permissions.get(action, False)


class OrganizationMember(models.Model):
    """
    Organization membership model.
    Links users to organizations with roles.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='members'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='organization_memberships'
    )
    role = models.ForeignKey(
        Role,
        on_delete=models.PROTECT,
        related_name='members'
    )

    # Department
    department = models.ForeignKey(
        'Department',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='members'
    )

    # Member-specific permissions (override role permissions)
    custom_permissions = models.JSONField(default=dict, blank=True)

    # Status
    is_active = models.BooleanField(default=True, db_index=True)

    # Metadata
    title = models.CharField(max_length=100, null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    # Timestamps
    joined_at = models.DateTimeField(default=timezone.now, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'organization_members'
        verbose_name = 'Organization Member'
        verbose_name_plural = 'Organization Members'
        ordering = ['-joined_at']
        constraints = [
            models.UniqueConstraint(
                fields=['organization', 'user'],
                name='unique_user_per_organization'
            )
        ]
        indexes = [
            models.Index(fields=['organization', 'is_active']),
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['role']),
        ]

    def __str__(self):
        return f'{self.user.email} - {self.organization.name}'

    def has_permission(self, module, action):
        """
        Check if member has specific permission.
        Custom permissions override role permissions.

        Args:
            module: Module name
            action: Action name

        Returns:
            bool: True if member has permission
        """
        # Check custom permissions first
        if self.custom_permissions:
            module_permissions = self.custom_permissions.get(module, {})
            if action in module_permissions:
                return module_permissions[action]

        # Fall back to role permissions
        return self.role.has_permission(module, action)


class Department(models.Model):
    """
    Department model for organizing members within an organization.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='departments'
    )
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)

    # Hierarchy
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='sub_departments'
    )

    # Manager
    manager = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='managed_departments'
    )

    # Status
    is_active = models.BooleanField(default=True, db_index=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'departments'
        verbose_name = 'Department'
        verbose_name_plural = 'Departments'
        ordering = ['organization', 'name']
        constraints = [
            models.UniqueConstraint(
                fields=['organization', 'name'],
                name='unique_department_per_organization'
            )
        ]
        indexes = [
            models.Index(fields=['organization', 'is_active']),
        ]

    def __str__(self):
        return f'{self.organization.name} - {self.name}'


class Invitation(models.Model):
    """
    Invitation model for inviting users to organizations.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
        ('expired', 'Expired'),
        ('revoked', 'Revoked'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='invitations'
    )
    email = models.EmailField(max_length=255, db_index=True)
    role = models.ForeignKey(
        Role,
        on_delete=models.PROTECT,
        related_name='invitations'
    )

    # Invitation details
    invited_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='sent_invitations'
    )
    token = models.CharField(max_length=255, unique=True, db_index=True)

    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', db_index=True)

    # Metadata
    message = models.TextField(null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    # Timestamps
    expires_at = models.DateTimeField(db_index=True)
    accepted_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'invitations'
        verbose_name = 'Invitation'
        verbose_name_plural = 'Invitations'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['organization', 'status']),
            models.Index(fields=['email', 'status']),
            models.Index(fields=['token']),
            models.Index(fields=['expires_at']),
        ]

    def __str__(self):
        return f'{self.email} - {self.organization.name} - {self.status}'

    def is_expired(self):
        """Check if invitation is expired."""
        return timezone.now() > self.expires_at

    def is_valid(self):
        """Check if invitation is valid (pending and not expired)."""
        return self.status == 'pending' and not self.is_expired()


class UsageQuota(models.Model):
    """
    Usage quota model for tracking and limiting organization resource usage.
    """
    QUOTA_TYPE_CHOICES = [
        ('workflows', 'Workflows'),
        ('executions', 'Executions'),
        ('api_calls', 'API Calls'),
        ('storage', 'Storage (GB)'),
        ('members', 'Members'),
        ('ai_tokens', 'AI Tokens'),
        ('documents', 'Documents'),
    ]

    PERIOD_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
        ('total', 'Total'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='quotas'
    )
    quota_type = models.CharField(max_length=50, choices=QUOTA_TYPE_CHOICES, db_index=True)
    period = models.CharField(max_length=20, choices=PERIOD_CHOICES, default='monthly')

    # Limits
    limit = models.BigIntegerField(validators=[MinValueValidator(0)])
    current_usage = models.BigIntegerField(default=0, validators=[MinValueValidator(0)])

    # Alert thresholds (percentage)
    warning_threshold = models.IntegerField(default=80, validators=[MinValueValidator(0)])
    alert_threshold = models.IntegerField(default=95, validators=[MinValueValidator(0)])

    # Status
    is_active = models.BooleanField(default=True, db_index=True)
    is_enforced = models.BooleanField(default=True)  # Whether to block when limit is reached

    # Timestamps
    period_start = models.DateTimeField(default=timezone.now)
    period_end = models.DateTimeField(null=True, blank=True)
    last_reset_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'usage_quotas'
        verbose_name = 'Usage Quota'
        verbose_name_plural = 'Usage Quotas'
        ordering = ['organization', 'quota_type']
        constraints = [
            models.UniqueConstraint(
                fields=['organization', 'quota_type', 'period'],
                name='unique_quota_per_organization_type_period'
            )
        ]
        indexes = [
            models.Index(fields=['organization', 'quota_type']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return f'{self.organization.name} - {self.quota_type} - {self.period}'

    @property
    def usage_percentage(self):
        """Calculate usage percentage."""
        if self.limit == 0:
            return 0
        return (self.current_usage / self.limit) * 100

    @property
    def is_quota_exceeded(self):
        """Check if quota is exceeded."""
        return self.current_usage >= self.limit

    @property
    def is_warning_threshold_reached(self):
        """Check if warning threshold is reached."""
        return self.usage_percentage >= self.warning_threshold

    @property
    def is_alert_threshold_reached(self):
        """Check if alert threshold is reached."""
        return self.usage_percentage >= self.alert_threshold

    def increment_usage(self, amount=1):
        """
        Increment current usage.

        Args:
            amount: Amount to increment

        Raises:
            ValueError: If quota is exceeded and enforcement is enabled
        """
        if self.is_enforced and (self.current_usage + amount) > self.limit:
            raise ValueError(f'{self.quota_type} quota exceeded for {self.organization.name}')

        self.current_usage += amount
        self.save(update_fields=['current_usage', 'updated_at'])

    def reset_usage(self):
        """Reset current usage to 0."""
        self.current_usage = 0
        self.last_reset_at = timezone.now()
        self.save(update_fields=['current_usage', 'last_reset_at', 'updated_at'])
