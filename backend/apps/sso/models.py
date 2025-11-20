"""
SSO models for enterprise Single Sign-On functionality.
Supports OAuth 2.0, OIDC, and SAML 2.0 protocols.
"""
import uuid
from django.db import models
from django.utils import timezone
from django_cryptography.fields import encrypt


class SSOProvider(models.Model):
    """
    SSO provider configuration template.
    Defines available SSO providers (Google, Microsoft, Okta, etc.).
    """
    PROVIDER_TYPE_CHOICES = [
        ('oauth2', 'OAuth 2.0'),
        ('oidc', 'OpenID Connect'),
        ('saml2', 'SAML 2.0'),
    ]

    PROVIDER_NAME_CHOICES = [
        ('google', 'Google Workspace'),
        ('microsoft', 'Microsoft Azure AD'),
        ('okta', 'Okta'),
        ('onelogin', 'OneLogin'),
        ('auth0', 'Auth0'),
        ('generic_saml', 'Generic SAML 2.0'),
        ('generic_oidc', 'Generic OIDC'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    provider_type = models.CharField(max_length=20, choices=PROVIDER_TYPE_CHOICES, db_index=True)
    provider_name = models.CharField(max_length=50, choices=PROVIDER_NAME_CHOICES, db_index=True)

    # Display information
    display_name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    logo_url = models.URLField(max_length=500, null=True, blank=True)

    # Configuration
    is_enabled = models.BooleanField(default=True, db_index=True)
    is_default = models.BooleanField(default=False)
    requires_email_verification = models.BooleanField(default=False)

    # OAuth/OIDC specific fields
    authorization_url = models.URLField(max_length=500, null=True, blank=True)
    token_url = models.URLField(max_length=500, null=True, blank=True)
    userinfo_url = models.URLField(max_length=500, null=True, blank=True)
    jwks_url = models.URLField(max_length=500, null=True, blank=True)

    # SAML specific fields
    sso_url = models.URLField(max_length=500, null=True, blank=True)  # IdP SSO URL
    slo_url = models.URLField(max_length=500, null=True, blank=True)  # Single Logout URL
    entity_id = models.CharField(max_length=255, null=True, blank=True)  # IdP Entity ID

    # Additional configuration
    scopes = models.JSONField(default=list)  # OAuth/OIDC scopes
    metadata = models.JSONField(default=dict)  # Additional provider-specific config

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'sso_providers'
        verbose_name = 'SSO Provider'
        verbose_name_plural = 'SSO Providers'
        ordering = ['display_name']
        indexes = [
            models.Index(fields=['provider_type']),
            models.Index(fields=['provider_name']),
            models.Index(fields=['is_enabled']),
        ]

    def __str__(self):
        return self.display_name


class SSOConnection(models.Model):
    """
    Organization-specific SSO connection.
    Links an organization to an SSO provider with specific configuration.
    """
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('pending', 'Pending Configuration'),
        ('error', 'Error'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE,
        related_name='sso_connections'
    )
    provider = models.ForeignKey(
        SSOProvider,
        on_delete=models.PROTECT,
        related_name='connections'
    )

    # Connection details
    name = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', db_index=True)
    is_default = models.BooleanField(default=False)  # Default SSO for this organization

    # OAuth/OIDC credentials
    client_id = models.CharField(max_length=255, null=True, blank=True)
    client_secret_encrypted = encrypt(models.TextField(null=True, blank=True))
    redirect_uri = models.URLField(max_length=500, null=True, blank=True)

    # SAML configuration
    sp_entity_id = models.CharField(max_length=255, null=True, blank=True)  # Our SP Entity ID
    acs_url = models.URLField(max_length=500, null=True, blank=True)  # Assertion Consumer Service URL
    idp_metadata_url = models.URLField(max_length=500, null=True, blank=True)
    idp_metadata_xml = models.TextField(null=True, blank=True)  # Cached IdP metadata
    idp_certificate = models.TextField(null=True, blank=True)  # X.509 certificate

    # User provisioning settings
    auto_provision_users = models.BooleanField(default=True)
    auto_activate_users = models.BooleanField(default=True)
    require_email_verification = models.BooleanField(default=False)

    # Attribute mapping (IdP attributes -> FlowPilot fields)
    attribute_mapping = models.JSONField(
        default=dict,
        help_text="Maps IdP attributes to FlowPilot user fields"
    )

    # Role mapping (IdP groups/roles -> FlowPilot roles)
    role_mapping = models.JSONField(
        default=dict,
        help_text="Maps IdP groups to FlowPilot organization roles"
    )

    # Domain restrictions
    allowed_domains = models.JSONField(
        default=list,
        help_text="Allowed email domains for this SSO connection"
    )

    # Security settings
    enforce_sso = models.BooleanField(
        default=False,
        help_text="If true, users from this org must use SSO (disables password login)"
    )
    pkce_required = models.BooleanField(default=True, help_text="Require PKCE for OAuth flows")

    # Connection metadata
    metadata = models.JSONField(default=dict)
    last_sync_at = models.DateTimeField(null=True, blank=True)
    last_error = models.TextField(null=True, blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_sso_connections'
    )

    class Meta:
        db_table = 'sso_connections'
        verbose_name = 'SSO Connection'
        verbose_name_plural = 'SSO Connections'
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['organization', 'provider'],
                name='unique_org_provider_connection'
            )
        ]
        indexes = [
            models.Index(fields=['organization', 'status']),
            models.Index(fields=['provider']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f'{self.organization.name} - {self.provider.display_name}'

    @property
    def is_active(self):
        """Check if connection is active."""
        return self.status == 'active'


class SSOSession(models.Model):
    """
    SSO session tracking.
    Tracks active SSO sessions with IdP session information.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='sso_sessions'
    )
    connection = models.ForeignKey(
        SSOConnection,
        on_delete=models.CASCADE,
        related_name='sessions'
    )

    # Session identifiers
    session_id = models.CharField(max_length=255, unique=True, db_index=True)
    idp_session_id = models.CharField(max_length=255, null=True, blank=True)  # IdP's session ID

    # Session state
    state = models.CharField(max_length=255, null=True, blank=True)  # OAuth state parameter
    nonce = models.CharField(max_length=255, null=True, blank=True)  # OIDC nonce
    code_verifier = models.CharField(max_length=255, null=True, blank=True)  # PKCE code verifier

    # Session info
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)

    # Tokens (encrypted)
    access_token_encrypted = encrypt(models.TextField(null=True, blank=True))
    id_token_encrypted = encrypt(models.TextField(null=True, blank=True))
    refresh_token_encrypted = encrypt(models.TextField(null=True, blank=True))

    # Token expiration
    access_token_expires_at = models.DateTimeField(null=True, blank=True)
    refresh_token_expires_at = models.DateTimeField(null=True, blank=True)

    # Session status
    is_active = models.BooleanField(default=True, db_index=True)
    expires_at = models.DateTimeField(db_index=True)
    last_activity = models.DateTimeField(default=timezone.now)

    # Metadata
    metadata = models.JSONField(default=dict)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'sso_sessions'
        verbose_name = 'SSO Session'
        verbose_name_plural = 'SSO Sessions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['connection']),
            models.Index(fields=['session_id']),
            models.Index(fields=['is_active', 'expires_at']),
        ]

    def __str__(self):
        return f'{self.user.email} - {self.connection.provider.display_name}'

    def is_expired(self):
        """Check if session is expired."""
        return timezone.now() > self.expires_at

    def is_token_expired(self):
        """Check if access token is expired."""
        if not self.access_token_expires_at:
            return False
        return timezone.now() > self.access_token_expires_at


class SSOAuditLog(models.Model):
    """
    Comprehensive audit logging for SSO events.
    Tracks all SSO-related activities for security and compliance.
    """
    EVENT_TYPE_CHOICES = [
        # Authentication events
        ('login_initiated', 'SSO Login Initiated'),
        ('login_success', 'SSO Login Success'),
        ('login_failure', 'SSO Login Failure'),
        ('logout', 'SSO Logout'),

        # User provisioning events
        ('user_provisioned', 'User Auto-Provisioned'),
        ('user_updated', 'User Updated via SSO'),
        ('user_deactivated', 'User Deactivated'),

        # Connection events
        ('connection_created', 'SSO Connection Created'),
        ('connection_updated', 'SSO Connection Updated'),
        ('connection_deleted', 'SSO Connection Deleted'),
        ('connection_tested', 'SSO Connection Tested'),

        # Token events
        ('token_issued', 'Token Issued'),
        ('token_refreshed', 'Token Refreshed'),
        ('token_revoked', 'Token Revoked'),

        # Error events
        ('authentication_error', 'Authentication Error'),
        ('authorization_error', 'Authorization Error'),
        ('token_error', 'Token Error'),
        ('metadata_error', 'Metadata Error'),
        ('configuration_error', 'Configuration Error'),
    ]

    SEVERITY_CHOICES = [
        ('info', 'Info'),
        ('warning', 'Warning'),
        ('error', 'Error'),
        ('critical', 'Critical'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Event details
    event_type = models.CharField(max_length=50, choices=EVENT_TYPE_CHOICES, db_index=True)
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, default='info', db_index=True)
    message = models.TextField()

    # Related entities
    user = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sso_audit_logs'
    )
    connection = models.ForeignKey(
        SSOConnection,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs'
    )
    session = models.ForeignKey(
        SSOSession,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs'
    )
    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sso_audit_logs'
    )

    # Request context
    ip_address = models.GenericIPAddressField(null=True, blank=True, db_index=True)
    user_agent = models.TextField(null=True, blank=True)
    request_id = models.CharField(max_length=255, null=True, blank=True, db_index=True)

    # Additional data
    email = models.EmailField(max_length=255, null=True, blank=True, db_index=True)
    provider_name = models.CharField(max_length=100, null=True, blank=True)
    error_code = models.CharField(max_length=100, null=True, blank=True)
    error_details = models.JSONField(null=True, blank=True)
    metadata = models.JSONField(default=dict)

    # Timestamp
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = 'sso_audit_logs'
        verbose_name = 'SSO Audit Log'
        verbose_name_plural = 'SSO Audit Logs'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['event_type', '-created_at']),
            models.Index(fields=['severity', '-created_at']),
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['organization', '-created_at']),
            models.Index(fields=['ip_address', '-created_at']),
            models.Index(fields=['email', '-created_at']),
        ]

    def __str__(self):
        return f'{self.event_type} - {self.created_at}'

    @classmethod
    def log_event(cls, event_type, message, **kwargs):
        """
        Log an SSO event.

        Args:
            event_type: Type of event
            message: Event message
            **kwargs: Additional fields (user, connection, session, etc.)

        Returns:
            SSOAuditLog instance
        """
        log = cls(
            event_type=event_type,
            message=message,
            **kwargs
        )
        log.save()
        return log


class SSOStateToken(models.Model):
    """
    Temporary state tokens for OAuth/OIDC flows.
    Used for CSRF protection and PKCE.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    token = models.CharField(max_length=255, unique=True, db_index=True)

    # OAuth/OIDC state
    state = models.CharField(max_length=255, unique=True)
    nonce = models.CharField(max_length=255, null=True, blank=True)
    code_verifier = models.CharField(max_length=255, null=True, blank=True)  # PKCE
    code_challenge = models.CharField(max_length=255, null=True, blank=True)  # PKCE

    # Flow context
    connection = models.ForeignKey(
        SSOConnection,
        on_delete=models.CASCADE,
        related_name='state_tokens'
    )
    redirect_uri = models.URLField(max_length=500, null=True, blank=True)

    # Security
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)

    # Status
    is_used = models.BooleanField(default=False, db_index=True)
    used_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(db_index=True)

    # Metadata
    metadata = models.JSONField(default=dict)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'sso_state_tokens'
        verbose_name = 'SSO State Token'
        verbose_name_plural = 'SSO State Tokens'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['token', 'is_used']),
            models.Index(fields=['state']),
            models.Index(fields=['expires_at']),
        ]

    def __str__(self):
        return f'{self.token[:10]}... - {self.connection}'

    def is_valid(self):
        """Check if token is valid (not used and not expired)."""
        if self.is_used:
            return False
        if timezone.now() > self.expires_at:
            return False
        return True

    @staticmethod
    def generate_token():
        """Generate a secure random token."""
        import secrets
        return secrets.token_urlsafe(32)

    @staticmethod
    def generate_state():
        """Generate a secure state parameter."""
        import secrets
        return secrets.token_urlsafe(32)

    @staticmethod
    def generate_nonce():
        """Generate a secure nonce."""
        import secrets
        return secrets.token_urlsafe(16)

    @staticmethod
    def generate_pkce_pair():
        """
        Generate PKCE code verifier and challenge.

        Returns:
            tuple: (code_verifier, code_challenge)
        """
        import secrets
        import hashlib
        import base64

        code_verifier = secrets.token_urlsafe(64)[:128]
        code_challenge = base64.urlsafe_b64encode(
            hashlib.sha256(code_verifier.encode()).digest()
        ).decode().rstrip('=')

        return code_verifier, code_challenge
