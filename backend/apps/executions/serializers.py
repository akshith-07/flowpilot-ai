"""
Serializers for Execution models.
"""
from rest_framework import serializers
from .models import WorkflowExecution, ExecutionStep, ExecutionLog, AIRequest


class ExecutionLogSerializer(serializers.ModelSerializer):
    """Serializer for ExecutionLog model."""

    class Meta:
        model = ExecutionLog
        fields = [
            'id', 'execution', 'step', 'level', 'message',
            'details', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class AIRequestSerializer(serializers.ModelSerializer):
    """Serializer for AIRequest model."""

    class Meta:
        model = AIRequest
        fields = [
            'id', 'execution', 'step', 'provider', 'model', 'prompt',
            'response', 'system_prompt', 'input_tokens', 'output_tokens',
            'total_tokens', 'cost', 'duration', 'success', 'error_message',
            'metadata', 'created_at'
        ]
        read_only_fields = ['id', 'total_tokens', 'created_at']


class ExecutionStepSerializer(serializers.ModelSerializer):
    """Serializer for ExecutionStep model."""

    logs = ExecutionLogSerializer(many=True, read_only=True)
    ai_requests = AIRequestSerializer(many=True, read_only=True)

    class Meta:
        model = ExecutionStep
        fields = [
            'id', 'execution', 'node_id', 'node_type', 'node_name',
            'step_number', 'status', 'input_data', 'output_data',
            'error_message', 'error_details', 'started_at', 'completed_at',
            'duration', 'retry_count', 'metadata', 'logs', 'ai_requests',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ExecutionStepListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for step lists."""

    class Meta:
        model = ExecutionStep
        fields = [
            'id', 'node_id', 'node_name', 'step_number', 'status',
            'started_at', 'completed_at', 'duration'
        ]
        read_only_fields = fields


class WorkflowExecutionSerializer(serializers.ModelSerializer):
    """Serializer for WorkflowExecution model."""

    workflow_name = serializers.CharField(source='workflow.name', read_only=True)
    triggered_by_email = serializers.EmailField(source='triggered_by.email', read_only=True)
    trigger_name = serializers.CharField(source='trigger.name', read_only=True)
    steps = ExecutionStepListSerializer(many=True, read_only=True)
    logs = ExecutionLogSerializer(many=True, read_only=True)

    class Meta:
        model = WorkflowExecution
        fields = [
            'id', 'workflow', 'workflow_name', 'status', 'input_data',
            'output_data', 'error_message', 'error_details', 'context',
            'trigger', 'trigger_name', 'triggered_by', 'triggered_by_email',
            'started_at', 'completed_at', 'duration', 'memory_usage',
            'cpu_time', 'ai_tokens_used', 'ai_cost', 'retry_count',
            'max_retries', 'parent_execution', 'metadata', 'steps', 'logs',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'started_at', 'completed_at', 'duration', 'created_at',
            'updated_at'
        ]


class WorkflowExecutionListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for execution lists."""

    workflow_name = serializers.CharField(source='workflow.name', read_only=True)
    triggered_by_email = serializers.EmailField(source='triggered_by.email', read_only=True)

    class Meta:
        model = WorkflowExecution
        fields = [
            'id', 'workflow_name', 'status', 'triggered_by_email',
            'started_at', 'completed_at', 'duration', 'ai_cost',
            'created_at'
        ]
        read_only_fields = fields


class ExecutionRetrySerializer(serializers.Serializer):
    """Serializer for retrying executions."""

    execution_id = serializers.UUIDField(required=True)
