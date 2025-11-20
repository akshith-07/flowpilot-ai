"""
Django admin configuration for Workflows app.
"""
from django.contrib import admin
from .models import (
    Workflow, WorkflowVersion, WorkflowTemplate,
    WorkflowVariable, WorkflowTrigger
)


@admin.register(WorkflowTemplate)
class WorkflowTemplateAdmin(admin.ModelAdmin):
    """Admin for WorkflowTemplate model."""

    list_display = [
        'name', 'category', 'is_public', 'is_featured',
        'use_count', 'created_by', 'created_at'
    ]
    list_filter = ['category', 'is_public', 'is_featured', 'created_at']
    search_fields = ['name', 'description', 'tags']
    readonly_fields = ['id', 'use_count', 'created_at', 'updated_at']
    prepopulated_fields = {'slug': ('name',)}
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'name', 'slug', 'category', 'description')
        }),
        ('Template Data', {
            'fields': ('definition', 'thumbnail_url', 'tags')
        }),
        ('Visibility', {
            'fields': ('is_public', 'is_featured')
        }),
        ('Statistics', {
            'fields': ('use_count', 'created_by')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Workflow)
class WorkflowAdmin(admin.ModelAdmin):
    """Admin for Workflow model."""

    list_display = [
        'name', 'organization', 'status', 'is_active', 'version',
        'execution_count', 'success_rate_display', 'created_at'
    ]
    list_filter = ['status', 'is_active', 'created_at', 'updated_at']
    search_fields = ['name', 'description', 'organization__name', 'tags']
    readonly_fields = [
        'id', 'version', 'execution_count', 'success_count',
        'failure_count', 'success_rate', 'last_executed_at',
        'created_at', 'updated_at'
    ]
    fieldsets = (
        ('Basic Information', {
            'fields': (
                'id', 'organization', 'name', 'description',
                'template'
            )
        }),
        ('Workflow Definition', {
            'fields': ('definition',)
        }),
        ('Status', {
            'fields': ('status', 'is_active')
        }),
        ('Versioning', {
            'fields': ('version', 'current_version')
        }),
        ('Metadata', {
            'fields': ('tags', 'metadata'),
            'classes': ('collapse',)
        }),
        ('Statistics', {
            'fields': (
                'execution_count', 'success_count', 'failure_count',
                'success_rate', 'last_executed_at'
            )
        }),
        ('Ownership', {
            'fields': ('created_by', 'updated_by')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def success_rate_display(self, obj):
        """Display success rate."""
        return f'{obj.success_rate:.2f}%'
    success_rate_display.short_description = 'Success Rate'


@admin.register(WorkflowVersion)
class WorkflowVersionAdmin(admin.ModelAdmin):
    """Admin for WorkflowVersion model."""

    list_display = [
        'workflow', 'version_number', 'created_by', 'created_at'
    ]
    list_filter = ['created_at']
    search_fields = ['workflow__name', 'change_summary']
    readonly_fields = ['id', 'created_at']
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'workflow', 'version_number')
        }),
        ('Version Data', {
            'fields': ('definition', 'change_summary', 'metadata')
        }),
        ('Author', {
            'fields': ('created_by',)
        }),
        ('Timestamp', {
            'fields': ('created_at',)
        }),
    )


@admin.register(WorkflowVariable)
class WorkflowVariableAdmin(admin.ModelAdmin):
    """Admin for WorkflowVariable model."""

    list_display = [
        'workflow', 'name', 'variable_type', 'scope',
        'is_required', 'is_secret', 'created_at'
    ]
    list_filter = ['variable_type', 'scope', 'is_required', 'is_secret']
    search_fields = ['workflow__name', 'name', 'description']
    readonly_fields = ['id', 'created_at', 'updated_at']
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'workflow', 'name', 'description')
        }),
        ('Type & Scope', {
            'fields': ('variable_type', 'scope')
        }),
        ('Value', {
            'fields': ('default_value', 'is_required', 'is_secret')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(WorkflowTrigger)
class WorkflowTriggerAdmin(admin.ModelAdmin):
    """Admin for WorkflowTrigger model."""

    list_display = [
        'workflow', 'name', 'trigger_type', 'is_active',
        'execution_count', 'last_triggered_at', 'created_at'
    ]
    list_filter = ['trigger_type', 'is_active', 'created_at']
    search_fields = ['workflow__name', 'name']
    readonly_fields = [
        'id', 'webhook_url', 'execution_count',
        'last_triggered_at', 'created_at', 'updated_at'
    ]
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'workflow', 'name', 'trigger_type')
        }),
        ('Configuration', {
            'fields': ('config',)
        }),
        ('Scheduled Trigger', {
            'fields': ('cron_expression', 'timezone'),
            'classes': ('collapse',)
        }),
        ('Webhook Trigger', {
            'fields': ('webhook_url', 'webhook_secret'),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Statistics', {
            'fields': ('execution_count', 'last_triggered_at')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
