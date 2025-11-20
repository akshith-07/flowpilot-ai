"""
SSO admin interface.
"""
from django.contrib import admin
from django.utils.html import format_html
from .models import (
    SSOProvider, SSOConnection, SSOSession,
    SSOAuditLog, SSOStateToken
)


@admin.register(SSOProvider)
class SSOProviderAdmin(admin.ModelAdmin):
    """Admin for SSO Provider."""

    list_display = [
        'display_name', 'provider_type', 'provider_name',
        'is_enabled', 'is_default', 'created_at'
    ]
    list_filter = ['provider_type', 'provider_name', 'is_enabled', 'is_default']
    search_fields = ['name', 'display_name', 'entity_id']
    readonly_fields = ['id', 'created_at', 'updated_at']
    ordering = ['display_name']

    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'name', 'provider_type', 'provider_name', 'display_name', 'description', 'logo_url')
        }),
        ('Configuration', {
            'fields': ('is_enabled', 'is_default', 'requires_email_verification')
        }),
        ('OAuth/OIDC Settings', {
            'fields': ('authorization_url', 'token_url', 'userinfo_url', 'jwks_url', 'scopes'),
            'classes': ('collapse',)
        }),
        ('SAML Settings', {
            'fields': ('sso_url', 'slo_url', 'entity_id'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('metadata',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(SSOConnection)
class SSOConnectionAdmin(admin.ModelAdmin):
    """Admin for SSO Connection."""

    list_display = [
        'name', 'organization', 'provider_display',
        'status_badge', 'is_default', 'auto_provision_users',
        'created_at'
    ]
    list_filter = [
        'status', 'provider__provider_type', 'is_default',
        'auto_provision_users', 'enforce_sso', 'created_at'
    ]
    search_fields = ['name', 'organization__name', 'client_id', 'sp_entity_id']
    readonly_fields = ['id', 'created_at', 'updated_at', 'created_by', 'last_sync_at']
    autocomplete_fields = ['organization', 'provider', 'created_by']
    ordering = ['-created_at']

    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'organization', 'provider', 'name', 'status', 'is_default')
        }),
        ('OAuth/OIDC Configuration', {
            'fields': ('client_id', 'redirect_uri', 'pkce_required'),
            'classes': ('collapse',)
        }),
        ('SAML Configuration', {
            'fields': ('sp_entity_id', 'acs_url', 'idp_metadata_url'),
            'classes': ('collapse',)
        }),
        ('User Provisioning', {
            'fields': (
                'auto_provision_users', 'auto_activate_users',
                'require_email_verification', 'attribute_mapping',
                'role_mapping', 'allowed_domains'
            ),
            'classes': ('collapse',)
        }),
        ('Security Settings', {
            'fields': ('enforce_sso',),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('metadata', 'last_sync_at', 'last_error'),
            'classes': ('collapse',)
        }),
        ('Audit Information', {
            'fields': ('created_at', 'updated_at', 'created_by'),
            'classes': ('collapse',)
        }),
    )

    def provider_display(self, obj):
        """Display provider name."""
        return obj.provider.display_name
    provider_display.short_description = 'Provider'

    def status_badge(self, obj):
        """Display status as colored badge."""
        colors = {
            'active': 'green',
            'inactive': 'gray',
            'pending': 'orange',
            'error': 'red'
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'


@admin.register(SSOSession)
class SSOSessionAdmin(admin.ModelAdmin):
    """Admin for SSO Session."""

    list_display = [
        'user_email', 'connection_name', 'provider_name',
        'is_active_badge', 'ip_address', 'created_at', 'expires_at'
    ]
    list_filter = ['is_active', 'connection__provider', 'created_at']
    search_fields = ['user__email', 'session_id', 'ip_address']
    readonly_fields = [
        'id', 'session_id', 'created_at', 'updated_at',
        'access_token_expires_at', 'last_activity'
    ]
    autocomplete_fields = ['user', 'connection']
    ordering = ['-created_at']
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Session Information', {
            'fields': ('id', 'user', 'connection', 'session_id', 'idp_session_id')
        }),
        ('Session State', {
            'fields': ('is_active', 'expires_at', 'last_activity')
        }),
        ('Request Context', {
            'fields': ('ip_address', 'user_agent'),
            'classes': ('collapse',)
        }),
        ('Token Information', {
            'fields': ('access_token_expires_at', 'refresh_token_expires_at'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('metadata',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def user_email(self, obj):
        """Display user email."""
        return obj.user.email
    user_email.short_description = 'User'

    def connection_name(self, obj):
        """Display connection name."""
        return obj.connection.name
    connection_name.short_description = 'Connection'

    def provider_name(self, obj):
        """Display provider name."""
        return obj.connection.provider.display_name
    provider_name.short_description = 'Provider'

    def is_active_badge(self, obj):
        """Display active status as badge."""
        if obj.is_active:
            return format_html('<span style="color: green; font-weight: bold;">Active</span>')
        return format_html('<span style="color: gray; font-weight: bold;">Inactive</span>')
    is_active_badge.short_description = 'Status'


@admin.register(SSOAuditLog)
class SSOAuditLogAdmin(admin.ModelAdmin):
    """Admin for SSO Audit Log."""

    list_display = [
        'event_type', 'severity_badge', 'email',
        'provider_name', 'ip_address', 'created_at'
    ]
    list_filter = ['event_type', 'severity', 'provider_name', 'created_at']
    search_fields = ['email', 'message', 'ip_address', 'request_id', 'error_code']
    readonly_fields = [
        'id', 'event_type', 'severity', 'message',
        'user', 'connection', 'session', 'organization',
        'ip_address', 'user_agent', 'request_id',
        'email', 'provider_name', 'error_code',
        'error_details', 'metadata', 'created_at'
    ]
    ordering = ['-created_at']
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Event Information', {
            'fields': ('id', 'event_type', 'severity', 'message')
        }),
        ('Related Entities', {
            'fields': ('user', 'connection', 'session', 'organization', 'email'),
            'classes': ('collapse',)
        }),
        ('Request Context', {
            'fields': ('ip_address', 'user_agent', 'request_id'),
            'classes': ('collapse',)
        }),
        ('Error Details', {
            'fields': ('provider_name', 'error_code', 'error_details'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('metadata',),
            'classes': ('collapse',)
        }),
        ('Timestamp', {
            'fields': ('created_at',)
        }),
    )

    def has_add_permission(self, request):
        """Disable manual creation of audit logs."""
        return False

    def has_change_permission(self, request, obj=None):
        """Make audit logs read-only."""
        return False

    def has_delete_permission(self, request, obj=None):
        """Disable deletion of audit logs."""
        return False

    def severity_badge(self, obj):
        """Display severity as colored badge."""
        colors = {
            'info': 'blue',
            'warning': 'orange',
            'error': 'red',
            'critical': 'darkred'
        }
        color = colors.get(obj.severity, 'gray')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_severity_display().upper()
        )
    severity_badge.short_description = 'Severity'


@admin.register(SSOStateToken)
class SSOStateTokenAdmin(admin.ModelAdmin):
    """Admin for SSO State Token."""

    list_display = [
        'token_short', 'connection', 'is_used',
        'expires_at', 'created_at'
    ]
    list_filter = ['is_used', 'created_at', 'expires_at']
    search_fields = ['token', 'state']
    readonly_fields = [
        'id', 'token', 'state', 'nonce',
        'code_verifier', 'code_challenge',
        'connection', 'redirect_uri',
        'ip_address', 'user_agent',
        'is_used', 'used_at', 'expires_at',
        'metadata', 'created_at'
    ]
    ordering = ['-created_at']

    fieldsets = (
        ('Token Information', {
            'fields': ('id', 'token', 'state', 'nonce')
        }),
        ('PKCE', {
            'fields': ('code_verifier', 'code_challenge'),
            'classes': ('collapse',)
        }),
        ('Flow Context', {
            'fields': ('connection', 'redirect_uri')
        }),
        ('Security', {
            'fields': ('ip_address', 'user_agent'),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('is_used', 'used_at', 'expires_at')
        }),
        ('Metadata', {
            'fields': ('metadata',),
            'classes': ('collapse',)
        }),
        ('Timestamp', {
            'fields': ('created_at',)
        }),
    )

    def has_add_permission(self, request):
        """Disable manual creation of state tokens."""
        return False

    def has_change_permission(self, request, obj=None):
        """Make state tokens read-only."""
        return False

    def token_short(self, obj):
        """Display shortened token."""
        return f'{obj.token[:20]}...'
    token_short.short_description = 'Token'
