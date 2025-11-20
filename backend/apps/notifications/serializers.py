"""
Serializers for Notifications app.
"""
from rest_framework import serializers
from .models import Notification, NotificationPreference, AlertRule


class NotificationSerializer(serializers.ModelSerializer):
    """Serializer for Notification model."""

    recipient_email = serializers.EmailField(source='recipient.email', read_only=True)

    class Meta:
        model = Notification
        fields = [
            'id', 'organization', 'recipient', 'recipient_email', 'title',
            'message', 'notification_type', 'channel', 'is_read',
            'read_at', 'sent_at', 'metadata', 'created_at'
        ]
        read_only_fields = ['id', 'organization', 'sent_at', 'created_at']


class NotificationPreferenceSerializer(serializers.ModelSerializer):
    """Serializer for NotificationPreference model."""

    class Meta:
        model = NotificationPreference
        fields = [
            'id', 'user', 'notification_type', 'email_enabled',
            'slack_enabled', 'in_app_enabled', 'sms_enabled',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']


class AlertRuleSerializer(serializers.ModelSerializer):
    """Serializer for AlertRule model."""

    class Meta:
        model = AlertRule
        fields = [
            'id', 'organization', 'name', 'description', 'rule_type',
            'conditions', 'actions', 'is_active', 'last_triggered_at',
            'trigger_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'organization', 'last_triggered_at', 'trigger_count', 'created_at', 'updated_at']


class NotificationMarkReadSerializer(serializers.Serializer):
    """Serializer for marking notifications as read."""

    notification_ids = serializers.ListField(
        child=serializers.UUIDField(),
        help_text='List of notification IDs to mark as read'
    )
