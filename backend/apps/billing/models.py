"""
Billing models for FlowPilot AI.
Handles usage tracking and quotas.
"""
import uuid
import secrets
from django.db import models
from django.contrib.auth import get_user_model
from apps.organizations.models import Organization

User = get_user_model()


class BillingUsage(models.Model):
    """Track billable usage for organizations."""

    USAGE_TYPE_CHOICES = [
        ('workflow_execution', 'Workflow Execution'),
        ('ai_tokens', 'AI Tokens'),
        ('api_call', 'API Call'),
        ('storage', 'Storage'),
        ('document_processing', 'Document Processing'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='billing_usage')
    usage_type = models.CharField(max_length=50, choices=USAGE_TYPE_CHOICES, db_index=True)
    quantity = models.BigIntegerField()  # Quantity used
    unit_cost = models.DecimalField(max_digits=10, decimal_places=6, default=0)
    total_cost = models.DecimalField(max_digits=10, decimal_places=4, default=0)
    resource_id = models.CharField(max_length=255, null=True, blank=True)  # Reference to workflow, execution, etc.
    metadata = models.JSONField(default=dict, blank=True)
    billing_period_start = models.DateField()
    billing_period_end = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = 'billing_usage'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['organization', 'usage_type', '-created_at']),
            models.Index(fields=['billing_period_start', 'billing_period_end']),
        ]

    def __str__(self):
        return f'{self.organization.name} - {self.usage_type} - {self.quantity}'

    def save(self, *args, **kwargs):
        """Calculate total cost on save."""
        self.total_cost = self.quantity * self.unit_cost
        super().save(*args, **kwargs)


class SubscriptionPlan(models.Model):
    """Subscription plans configuration."""

    TIER_CHOICES = [
        ('free', 'Free'),
        ('starter', 'Starter'),
        ('professional', 'Professional'),
        ('enterprise', 'Enterprise'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    tier = models.CharField(max_length=20, choices=TIER_CHOICES, unique=True)
    description = models.TextField()
    monthly_price = models.DecimalField(max_digits=10, decimal_places=2)
    annual_price = models.DecimalField(max_digits=10, decimal_places=2)

    # Limits
    max_workflows = models.IntegerField()
    max_executions_per_month = models.IntegerField()
    max_ai_tokens_per_month = models.BigIntegerField()
    max_storage_gb = models.IntegerField()
    max_members = models.IntegerField()

    features = models.JSONField(default=list)  # List of features
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'subscription_plans'
        ordering = ['monthly_price']

    def __str__(self):
        return f'{self.name} ({self.tier})'


class OrganizationSubscription(models.Model):
    """Organization subscription status."""

    STATUS_CHOICES = [
        ('active', 'Active'),
        ('cancelled', 'Cancelled'),
        ('expired', 'Expired'),
        ('trial', 'Trial'),
    ]

    BILLING_CYCLE_CHOICES = [
        ('monthly', 'Monthly'),
        ('annual', 'Annual'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.OneToOneField(Organization, on_delete=models.CASCADE, related_name='subscription')
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.PROTECT, related_name='subscriptions')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='trial', db_index=True)
    billing_cycle = models.CharField(max_length=20, choices=BILLING_CYCLE_CHOICES, default='monthly')

    # Billing details
    current_period_start = models.DateField()
    current_period_end = models.DateField()
    trial_end_date = models.DateField(null=True, blank=True)

    # Payment
    stripe_customer_id = models.CharField(max_length=255, null=True, blank=True)
    stripe_subscription_id = models.CharField(max_length=255, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'organization_subscriptions'

    def __str__(self):
        return f'{self.organization.name} - {self.plan.name}'


class Invoice(models.Model):
    """Billing invoices."""

    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='invoices')
    invoice_number = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', db_index=True)

    # Amounts
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2)

    # Billing period
    period_start = models.DateField()
    period_end = models.DateField()

    # Payment
    stripe_invoice_id = models.CharField(max_length=255, null=True, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    due_date = models.DateField()

    # Line items
    line_items = models.JSONField(default=list)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'invoices'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['organization', '-created_at']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f'{self.invoice_number} - {self.organization.name}'


class APIKey(models.Model):
    """
    API Key for programmatic access.
    Allows external systems to authenticate and make API requests.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='api_keys')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_api_keys')

    # Key details
    name = models.CharField(max_length=255, help_text="Descriptive name for the API key")
    key = models.CharField(max_length=255, unique=True, db_index=True, editable=False)
    prefix = models.CharField(max_length=16, editable=False, help_text="First 8 characters for display")

    # Permissions and scope
    permissions = models.JSONField(default=list, blank=True, help_text="List of allowed permissions")
    allowed_ips = models.JSONField(default=list, blank=True, help_text="IP whitelist (empty = allow all)")

    # Status
    is_active = models.BooleanField(default=True, db_index=True)
    expires_at = models.DateTimeField(null=True, blank=True, help_text="Expiration date (null = no expiry)")
    last_used_at = models.DateTimeField(null=True, blank=True)

    # Metadata
    description = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'api_keys'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['organization', '-created_at']),
            models.Index(fields=['key', 'is_active']),
        ]
        verbose_name = 'API Key'
        verbose_name_plural = 'API Keys'

    def __str__(self):
        return f'{self.name} ({self.prefix}...)'

    def save(self, *args, **kwargs):
        """Generate API key on creation."""
        if not self.key:
            self.key = self.generate_key()
            self.prefix = self.key[:8]
        super().save(*args, **kwargs)

    @staticmethod
    def generate_key():
        """Generate a secure random API key."""
        return f'fp_{secrets.token_urlsafe(48)}'

    def rotate_key(self):
        """Rotate the API key (generate a new one)."""
        old_key = self.key
        self.key = self.generate_key()
        self.prefix = self.key[:8]
        self.save(update_fields=['key', 'prefix', 'updated_at'])
        return old_key, self.key
