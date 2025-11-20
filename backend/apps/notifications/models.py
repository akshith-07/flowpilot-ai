"""
Notification models for FlowPilot AI.
Handles multi-channel notifications.
"""
import uuid
from django.db import models
from django.contrib.auth import get_user_model
from apps.organizations.models import Organization

User = get_user_model()


class Notification(models.Model):
    """Notification messages."""

    TYPE_CHOICES = [
        ('info', 'Info'),
        ('success', 'Success'),
        ('warning', 'Warning'),
        ('error', 'Error'),
    ]

    CHANNEL_CHOICES = [
        ('in_app', 'In-App'),
        ('email', 'Email'),
        ('slack', 'Slack'),
        ('teams', 'Teams'),
        ('sms', 'SMS'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='notifications', null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications', null=True, blank=True)
    title = models.CharField(max_length=255)
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='info')
    channels = models.JSONField(default=list)  # List of channels to send to
    metadata = models.JSONField(default=dict, blank=True)
    is_read = models.BooleanField(default=False, db_index=True)
    read_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = 'notifications'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_read', '-created_at']),
            models.Index(fields=['organization', '-created_at']),
        ]

    def __str__(self):
        return f'{self.title} - {self.notification_type}'


class NotificationPreference(models.Model):
    """User notification preferences."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='notification_preferences')
    email_enabled = models.BooleanField(default=True)
    slack_enabled = models.BooleanField(default=False)
    sms_enabled = models.BooleanField(default=False)
    in_app_enabled = models.BooleanField(default=True)
    preferences = models.JSONField(default=dict, blank=True)  # Custom preferences
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'notification_preferences'


class AlertRule(models.Model):
    """Alert rules for automated notifications."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='alert_rules')
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    trigger_condition = models.JSONField()  # Condition to trigger alert
    channels = models.JSONField(default=list)
    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'alert_rules'
