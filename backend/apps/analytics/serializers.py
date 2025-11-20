"""
Serializers for Analytics app.
"""
from rest_framework import serializers
from .models import DailyMetrics, UserActivity, ErrorLog


class DailyMetricsSerializer(serializers.ModelSerializer):
    """Serializer for DailyMetrics model."""

    class Meta:
        model = DailyMetrics
        fields = [
            'id', 'organization', 'date', 'active_users', 'workflow_executions',
            'successful_executions', 'failed_executions', 'ai_requests',
            'ai_tokens_used', 'ai_cost', 'documents_processed',
            'api_requests', 'storage_used_bytes', 'metadata', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class UserActivitySerializer(serializers.ModelSerializer):
    """Serializer for UserActivity model."""

    user_email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = UserActivity
        fields = [
            'id', 'user', 'user_email', 'organization', 'action',
            'resource_type', 'resource_id', 'metadata', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class ErrorLogSerializer(serializers.ModelSerializer):
    """Serializer for ErrorLog model."""

    class Meta:
        model = ErrorLog
        fields = [
            'id', 'organization', 'error_type', 'error_message',
            'stack_trace', 'severity', 'context', 'user',
            'resolved', 'resolved_at', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class DashboardMetricsSerializer(serializers.Serializer):
    """Serializer for dashboard metrics response."""

    period = serializers.ChoiceField(choices=['today', 'week', 'month', 'year'])
    active_users = serializers.IntegerField()
    total_workflows = serializers.IntegerField()
    total_executions = serializers.IntegerField()
    success_rate = serializers.FloatField()
    ai_requests = serializers.IntegerField()
    ai_cost = serializers.DecimalField(max_digits=10, decimal_places=2)


class WorkflowAnalyticsSerializer(serializers.Serializer):
    """Serializer for workflow analytics."""

    workflow_id = serializers.UUIDField()
    workflow_name = serializers.CharField()
    execution_count = serializers.IntegerField()
    success_count = serializers.IntegerField()
    failure_count = serializers.IntegerField()
    average_duration = serializers.FloatField()
    total_ai_cost = serializers.DecimalField(max_digits=10, decimal_places=2)
