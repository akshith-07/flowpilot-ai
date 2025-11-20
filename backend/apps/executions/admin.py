"""
Django admin configuration for Executions app.
"""
from django.contrib import admin
from .models import WorkflowExecution, ExecutionStep, ExecutionLog, AIRequest


@admin.register(WorkflowExecution)
class WorkflowExecutionAdmin(admin.ModelAdmin):
    """Admin for WorkflowExecution model."""

    list_display = [
        'workflow', 'status', 'triggered_by', 'started_at',
        'completed_at', 'duration', 'retry_count', 'created_at'
    ]
    list_filter = ['status', 'created_at', 'started_at']
    search_fields = ['workflow__name', 'triggered_by__email']
    readonly_fields = [
        'id', 'started_at', 'completed_at', 'duration',
        'memory_usage', 'cpu_time', 'ai_tokens_used', 'ai_cost',
        'created_at', 'updated_at'
    ]


@admin.register(ExecutionStep)
class ExecutionStepAdmin(admin.ModelAdmin):
    """Admin for ExecutionStep model."""

    list_display = [
        'execution', 'step_number', 'node_name', 'node_type',
        'status', 'duration', 'created_at'
    ]
    list_filter = ['status', 'node_type', 'created_at']
    search_fields = ['node_name', 'node_id']
    readonly_fields = ['id', 'started_at', 'completed_at', 'duration', 'created_at', 'updated_at']


@admin.register(ExecutionLog)
class ExecutionLogAdmin(admin.ModelAdmin):
    """Admin for ExecutionLog model."""

    list_display = ['execution', 'step', 'level', 'message_preview', 'created_at']
    list_filter = ['level', 'created_at']
    search_fields = ['message']
    readonly_fields = ['id', 'created_at']

    def message_preview(self, obj):
        return obj.message[:100]


@admin.register(AIRequest)
class AIRequestAdmin(admin.ModelAdmin):
    """Admin for AIRequest model."""

    list_display = [
        'execution', 'provider', 'model', 'total_tokens',
        'cost', 'success', 'created_at'
    ]
    list_filter = ['provider', 'success', 'created_at']
    search_fields = ['model', 'prompt']
    readonly_fields = ['id', 'total_tokens', 'created_at']
