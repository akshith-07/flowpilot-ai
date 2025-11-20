"""
User models for FlowPilot AI.
Includes User, UserSession, LoginAttempt, MFADevice, and OAuthConnection.
"""
import uuid
from django.contrib.auth.models.AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone
from django_cryptography.fields import encrypt
import pyotp


class UserManager(BaseUserManager):
    """Custom user manager."""

    def create_user(self, email, password=None, **extra_fields):
        """
        Create and save a regular user with the given email and password.

        Args:
            email: User email
            password: User password
            **extra_fields: Additional fields

        Returns:
            User instance
        """
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Create and save a superuser with the given email and password.

        Args:
            email: User email
            password: User password
            **extra_fields: Additional fields

        Returns:
            User instance
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('email_verified', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom user model with UUID primary key and email authentication.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(max_length=255, unique=True, db_index=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    # Status fields
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    # Email verification
    email_verified = models.BooleanField(default=False)
    email_verification_token = models.CharField(max_length=255, null=True, blank=True)

    # Phone
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    phone_verified = models.BooleanField(default=False)

    # Profile
    avatar_url = models.URLField(max_length=500, null=True, blank=True)
    timezone = models.CharField(max_length=50, default='UTC')
    locale = models.CharField(max_length=10, default='en')

    # Security
    last_login = models.DateTimeField(null=True, blank=True)
    password_changed_at = models.DateTimeField(default=timezone.now)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['email_verified']),
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        return self.email

    @property
    def full_name(self):
        """Return user's full name."""
        return f'{self.first_name} {self.last_name}'.strip()

    @property
    def is_mfa_enabled(self):
        """Check if user has MFA enabled."""
        return self.mfa_devices.filter(is_active=True, is_verified=True).exists()

    def needs_password_change(self):
        """
        Check if user needs to change password (based on expiration policy).

        Returns:
            bool: True if password needs to be changed
        """
        from django.conf import settings
        days = settings.PASSWORD_EXPIRATION_DAYS
        if not days:
            return False

        expiration_date = self.password_changed_at + timezone.timedelta(days=days)
        return timezone.now() > expiration_date


class UserSession(models.Model):
    """
    User session tracking with device information.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sessions')
    refresh_token_hash = models.CharField(max_length=255, db_index=True)

    # Device information
    device_name = models.CharField(max_length=255, null=True, blank=True)
    device_type = models.CharField(max_length=50, null=True, blank=True)  # 'web', 'mobile', 'desktop'
    browser = models.CharField(max_length=100, null=True, blank=True)
    os = models.CharField(max_length=100, null=True, blank=True)

    # Network information
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)

    # Status
    is_active = models.BooleanField(default=True, db_index=True)
    expires_at = models.DateTimeField(db_index=True)
    last_activity = models.DateTimeField(default=timezone.now)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'user_sessions'
        verbose_name = 'User Session'
        verbose_name_plural = 'User Sessions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['refresh_token_hash']),
            models.Index(fields=['expires_at']),
        ]

    def __str__(self):
        return f'{self.user.email} - {self.device_name or "Unknown Device"}'

    def is_expired(self):
        """Check if session is expired."""
        return timezone.now() > self.expires_at


class LoginAttempt(models.Model):
    """
    Login attempt tracking for security monitoring.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(max_length=255, db_index=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(null=True, blank=True)
    success = models.BooleanField(default=False, db_index=True)
    failure_reason = models.CharField(max_length=100, null=True, blank=True)
    attempted_at = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        db_table = 'login_attempts'
        verbose_name = 'Login Attempt'
        verbose_name_plural = 'Login Attempts'
        ordering = ['-attempted_at']
        indexes = [
            models.Index(fields=['email', '-attempted_at']),
            models.Index(fields=['ip_address', '-attempted_at']),
        ]

    def __str__(self):
        status = 'Success' if self.success else 'Failed'
        return f'{self.email} - {status} - {self.attempted_at}'

    @staticmethod
    def is_account_locked(email):
        """
        Check if account is locked due to failed login attempts.

        Args:
            email: User email

        Returns:
            bool: True if account is locked
        """
        from django.conf import settings
        max_attempts = settings.MAX_LOGIN_ATTEMPTS
        lockout_duration = settings.ACCOUNT_LOCKOUT_DURATION

        cutoff_time = timezone.now() - timezone.timedelta(minutes=lockout_duration)
        recent_failures = LoginAttempt.objects.filter(
            email=email,
            success=False,
            attempted_at__gte=cutoff_time
        ).count()

        return recent_failures >= max_attempts


class MFADevice(models.Model):
    """
    Multi-factor authentication device.
    """
    DEVICE_TYPE_CHOICES = [
        ('totp', 'TOTP (Authenticator App)'),
        ('sms', 'SMS'),
        ('backup_codes', 'Backup Codes'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mfa_devices')
    device_name = models.CharField(max_length=100)
    device_type = models.CharField(max_length=20, choices=DEVICE_TYPE_CHOICES, default='totp')

    # Encrypted secret
    secret_encrypted = encrypt(models.TextField())

    # Status
    is_active = models.BooleanField(default=True, db_index=True)
    is_verified = models.BooleanField(default=False, db_index=True)
    verified_at = models.DateTimeField(null=True, blank=True)
    last_used_at = models.DateTimeField(null=True, blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'mfa_devices'
        verbose_name = 'MFA Device'
        verbose_name_plural = 'MFA Devices'
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'device_type'],
                condition=models.Q(device_type='totp', is_active=True),
                name='unique_active_totp_per_user'
            )
        ]

    def __str__(self):
        return f'{self.user.email} - {self.device_name}'

    def verify_token(self, token):
        """
        Verify TOTP token.

        Args:
            token: TOTP token to verify

        Returns:
            bool: True if token is valid
        """
        if self.device_type != 'totp':
            return False

        totp = pyotp.TOTP(self.secret_encrypted)
        return totp.verify(token, valid_window=1)

    def get_provisioning_uri(self):
        """
        Get provisioning URI for QR code generation.

        Returns:
            str: Provisioning URI
        """
        if self.device_type != 'totp':
            return None

        totp = pyotp.TOTP(self.secret_encrypted)
        return totp.provisioning_uri(
            name=self.user.email,
            issuer_name='FlowPilot AI'
        )

    @staticmethod
    def generate_secret():
        """
        Generate a new TOTP secret.

        Returns:
            str: Base32-encoded secret
        """
        return pyotp.random_base32()


class OAuthConnection(models.Model):
    """
    OAuth 2.0 connection for SSO.
    """
    PROVIDER_CHOICES = [
        ('google', 'Google'),
        ('microsoft', 'Microsoft'),
        ('github', 'GitHub'),
        ('okta', 'Okta'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='oauth_connections')
    provider = models.CharField(max_length=50, choices=PROVIDER_CHOICES, db_index=True)
    provider_user_id = models.CharField(max_length=255)
    email = models.EmailField(max_length=255, null=True, blank=True)

    # Encrypted tokens
    access_token_encrypted = encrypt(models.TextField(null=True, blank=True))
    refresh_token_encrypted = encrypt(models.TextField(null=True, blank=True))

    expires_at = models.DateTimeField(null=True, blank=True)
    scopes = models.JSONField(default=list)
    metadata = models.JSONField(default=dict)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'oauth_connections'
        verbose_name = 'OAuth Connection'
        verbose_name_plural = 'OAuth Connections'
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['provider', 'provider_user_id'],
                name='unique_provider_user'
            )
        ]
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['provider']),
        ]

    def __str__(self):
        return f'{self.user.email} - {self.provider}'

    def is_token_expired(self):
        """Check if access token is expired."""
        if not self.expires_at:
            return False
        return timezone.now() > self.expires_at
