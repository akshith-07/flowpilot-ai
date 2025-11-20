"""
Connector models for FlowPilot AI.
Handles OAuth and third-party integrations.
"""
import uuid
from django.db import models
from django.utils import timezone
from django_cryptography.fields import encrypt
from apps.organizations.models import Organization


class Connector(models.Model):
    """Connector configuration for third-party services."""

    PROVIDER_CHOICES = [
        ('gmail', 'Gmail'),
        ('outlook', 'Outlook'),
        ('slack', 'Slack'),
        ('teams', 'Microsoft Teams'),
        ('notion', 'Notion'),
        ('trello', 'Trello'),
        ('jira', 'Jira'),
        ('salesforce', 'Salesforce'),
        ('hubspot', 'HubSpot'),
        ('google_drive', 'Google Drive'),
        ('dropbox', 'Dropbox'),
        ('custom', 'Custom'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='connectors')
    provider = models.CharField(max_length=50, choices=PROVIDER_CHOICES, db_index=True)
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    settings = models.JSONField(default=dict, blank=True)
    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'connectors'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.organization.name} - {self.provider}'


class ConnectorCredential(models.Model):
    """Encrypted credentials for connectors."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    connector = models.ForeignKey(Connector, on_delete=models.CASCADE, related_name='credentials')
    access_token_encrypted = encrypt(models.TextField(null=True, blank=True))
    refresh_token_encrypted = encrypt(models.TextField(null=True, blank=True))
    expires_at = models.DateTimeField(null=True, blank=True)
    scopes = models.JSONField(default=list, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'connector_credentials'

    def is_expired(self):
        return self.expires_at and timezone.now() > self.expires_at


class ConnectorWebhook(models.Model):
    """Webhook configurations for connectors."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    connector = models.ForeignKey(Connector, on_delete=models.CASCADE, related_name='webhooks')
    event_type = models.CharField(max_length=100)
    webhook_url = models.CharField(max_length=500, unique=True)
    webhook_secret = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'connector_webhooks'


class ConnectorSyncLog(models.Model):
    """Sync logs for connector operations."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    connector = models.ForeignKey(Connector, on_delete=models.CASCADE, related_name='sync_logs')
    operation = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=[('success', 'Success'), ('failed', 'Failed')])
    records_processed = models.IntegerField(default=0)
    error_message = models.TextField(null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'connector_sync_logs'
        ordering = ['-created_at']
