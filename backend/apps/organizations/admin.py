"""
Django admin configuration for Organizations app.
"""
from django.contrib import admin
from .models import (
    Organization, OrganizationMember, Role, Invitation,
    Department, UsageQuota
)


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    """Admin for Organization model."""

    list_display = [
        'name', 'slug', 'owner', 'is_active', 'member_count',
        'created_at'
    ]
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'slug', 'email', 'owner__email']
    readonly_fields = ['id', 'created_at', 'updated_at']
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'name', 'slug', 'parent', 'owner', 'description')
        }),
        ('Contact Information', {
            'fields': ('email', 'phone', 'website')
        }),
        ('Address', {
            'fields': (
                'address_line1', 'address_line2', 'city',
                'state', 'country', 'postal_code'
            )
        }),
        ('Branding & Settings', {
            'fields': ('logo_url', 'primary_color', 'timezone', 'locale')
        }),
        ('Data', {
            'fields': ('settings', 'metadata'),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    """Admin for Role model."""

    list_display = [
        'name', 'organization', 'role_type', 'is_system_role',
        'is_active', 'created_at'
    ]
    list_filter = ['role_type', 'is_system_role', 'is_active', 'created_at']
    search_fields = ['name', 'organization__name']
    readonly_fields = ['id', 'created_at', 'updated_at']
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'organization', 'name', 'role_type', 'description')
        }),
        ('Permissions', {
            'fields': ('permissions',)
        }),
        ('Status', {
            'fields': ('is_active', 'is_system_role')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(OrganizationMember)
class OrganizationMemberAdmin(admin.ModelAdmin):
    """Admin for OrganizationMember model."""

    list_display = [
        'user', 'organization', 'role', 'department',
        'is_active', 'joined_at'
    ]
    list_filter = ['is_active', 'role', 'department', 'joined_at']
    search_fields = [
        'user__email', 'user__first_name', 'user__last_name',
        'organization__name', 'title'
    ]
    readonly_fields = ['id', 'joined_at', 'created_at', 'updated_at']
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'organization', 'user', 'role', 'department')
        }),
        ('Details', {
            'fields': ('title', 'custom_permissions', 'metadata')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('joined_at', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    """Admin for Department model."""

    list_display = [
        'name', 'organization', 'parent', 'manager',
        'is_active', 'created_at'
    ]
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'organization__name', 'manager__email']
    readonly_fields = ['id', 'created_at', 'updated_at']
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'organization', 'name', 'description')
        }),
        ('Hierarchy', {
            'fields': ('parent', 'manager')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Invitation)
class InvitationAdmin(admin.ModelAdmin):
    """Admin for Invitation model."""

    list_display = [
        'email', 'organization', 'role', 'status',
        'invited_by', 'expires_at', 'created_at'
    ]
    list_filter = ['status', 'created_at', 'expires_at']
    search_fields = [
        'email', 'organization__name', 'invited_by__email'
    ]
    readonly_fields = [
        'id', 'token', 'accepted_at', 'created_at'
    ]
    fieldsets = (
        ('Basic Information', {
            'fields': (
                'id', 'organization', 'email', 'role',
                'invited_by', 'message'
            )
        }),
        ('Token & Status', {
            'fields': ('token', 'status')
        }),
        ('Metadata', {
            'fields': ('metadata',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('expires_at', 'accepted_at', 'created_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(UsageQuota)
class UsageQuotaAdmin(admin.ModelAdmin):
    """Admin for UsageQuota model."""

    list_display = [
        'organization', 'quota_type', 'period', 'current_usage',
        'limit', 'usage_percentage', 'is_active'
    ]
    list_filter = ['quota_type', 'period', 'is_active', 'is_enforced']
    search_fields = ['organization__name']
    readonly_fields = [
        'id', 'usage_percentage', 'is_quota_exceeded',
        'last_reset_at', 'created_at', 'updated_at'
    ]
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'organization', 'quota_type', 'period')
        }),
        ('Limits', {
            'fields': (
                'limit', 'current_usage', 'usage_percentage',
                'is_quota_exceeded'
            )
        }),
        ('Thresholds', {
            'fields': ('warning_threshold', 'alert_threshold')
        }),
        ('Status', {
            'fields': ('is_active', 'is_enforced')
        }),
        ('Period', {
            'fields': ('period_start', 'period_end', 'last_reset_at')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def usage_percentage(self, obj):
        """Display usage percentage."""
        return f'{obj.usage_percentage:.2f}%'
    usage_percentage.short_description = 'Usage %'
