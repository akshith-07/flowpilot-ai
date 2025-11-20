"""
Django admin configuration for Users app.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import User, UserSession, LoginAttempt, MFADevice, OAuthConnection, PasswordResetToken


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin configuration for User model."""

    list_display = [
        'email', 'full_name', 'is_active', 'is_staff',
        'email_verified', 'is_mfa_enabled_display', 'created_at'
    ]
    list_filter = [
        'is_active', 'is_staff', 'is_superuser',
        'email_verified', 'created_at'
    ]
    search_fields = ['email', 'first_name', 'last_name']
    ordering = ['-created_at']
    readonly_fields = [
        'id', 'last_login', 'created_at', 'updated_at',
        'password_changed_at'
    ]

    fieldsets = (
        ('Authentication', {
            'fields': ('id', 'email', 'password')
        }),
        ('Personal Info', {
            'fields': ('first_name', 'last_name', 'phone_number', 'avatar_url')
        }),
        ('Verification', {
            'fields': ('email_verified', 'email_verification_token', 'phone_verified')
        }),
        ('Preferences', {
            'fields': ('timezone', 'locale')
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('Important Dates', {
            'fields': ('last_login', 'password_changed_at', 'created_at', 'updated_at')
        }),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'password1', 'password2'),
        }),
    )

    def is_mfa_enabled_display(self, obj):
        """Display MFA status."""
        if obj.is_mfa_enabled:
            return format_html('<span style="color: green;">✓ Enabled</span>')
        return format_html('<span style="color: gray;">✗ Disabled</span>')
    is_mfa_enabled_display.short_description = 'MFA Status'


@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    """Admin configuration for UserSession model."""

    list_display = [
        'user', 'device_name', 'device_type', 'ip_address',
        'is_active', 'last_activity', 'created_at'
    ]
    list_filter = ['is_active', 'device_type', 'created_at']
    search_fields = ['user__email', 'ip_address', 'device_name']
    readonly_fields = [
        'id', 'user', 'refresh_token_hash', 'device_name', 'device_type',
        'browser', 'os', 'ip_address', 'user_agent', 'expires_at',
        'created_at', 'last_activity'
    ]
    ordering = ['-created_at']

    def has_add_permission(self, request):
        """Disable adding sessions via admin."""
        return False


@admin.register(LoginAttempt)
class LoginAttemptAdmin(admin.ModelAdmin):
    """Admin configuration for LoginAttempt model."""

    list_display = [
        'email', 'ip_address', 'success_display',
        'failure_reason', 'attempted_at'
    ]
    list_filter = ['success', 'failure_reason', 'attempted_at']
    search_fields = ['email', 'ip_address']
    readonly_fields = [
        'id', 'email', 'ip_address', 'user_agent',
        'success', 'failure_reason', 'attempted_at'
    ]
    ordering = ['-attempted_at']

    def success_display(self, obj):
        """Display success status with color."""
        if obj.success:
            return format_html('<span style="color: green;">✓ Success</span>')
        return format_html('<span style="color: red;">✗ Failed</span>')
    success_display.short_description = 'Status'

    def has_add_permission(self, request):
        """Disable adding login attempts via admin."""
        return False

    def has_change_permission(self, request, obj=None):
        """Disable editing login attempts."""
        return False

    def has_delete_permission(self, request, obj=None):
        """Disable deleting login attempts (audit trail)."""
        return False


@admin.register(MFADevice)
class MFADeviceAdmin(admin.ModelAdmin):
    """Admin configuration for MFADevice model."""

    list_display = [
        'user', 'device_name', 'device_type', 'is_active',
        'is_verified', 'verified_at', 'created_at'
    ]
    list_filter = ['device_type', 'is_active', 'is_verified', 'created_at']
    search_fields = ['user__email', 'device_name']
    readonly_fields = [
        'id', 'user', 'secret_encrypted', 'verified_at',
        'last_used_at', 'created_at'
    ]
    ordering = ['-created_at']


@admin.register(OAuthConnection)
class OAuthConnectionAdmin(admin.ModelAdmin):
    """Admin configuration for OAuthConnection model."""

    list_display = [
        'user', 'provider', 'email', 'created_at', 'updated_at'
    ]
    list_filter = ['provider', 'created_at']
    search_fields = ['user__email', 'email', 'provider_user_id']
    readonly_fields = [
        'id', 'user', 'provider', 'provider_user_id',
        'access_token_encrypted', 'refresh_token_encrypted',
        'expires_at', 'scopes', 'metadata', 'created_at', 'updated_at'
    ]
    ordering = ['-created_at']

    def has_add_permission(self, request):
        """Disable adding OAuth connections via admin."""
        return False


@admin.register(PasswordResetToken)
class PasswordResetTokenAdmin(admin.ModelAdmin):
    """Admin configuration for PasswordResetToken model."""

    list_display = [
        'user', 'token_preview', 'is_used', 'expires_at', 'created_at'
    ]
    list_filter = ['is_used', 'created_at']
    search_fields = ['user__email', 'token']
    readonly_fields = [
        'id', 'user', 'token', 'is_used', 'expires_at',
        'used_at', 'ip_address', 'user_agent', 'created_at'
    ]
    ordering = ['-created_at']

    def token_preview(self, obj):
        """Display preview of token."""
        return f'{obj.token[:10]}...'
    token_preview.short_description = 'Token'

    def has_add_permission(self, request):
        """Disable adding tokens via admin."""
        return False
