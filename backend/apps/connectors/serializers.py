"""
Serializers for Connectors app.
"""
from rest_framework import serializers
from .models import Connector, ConnectorCredential, ConnectorWebhook, ConnectorSyncLog


class ConnectorSerializer(serializers.ModelSerializer):
    """Serializer for Connector model."""

    class Meta:
        model = Connector
        fields = [
            'id', 'organization', 'name', 'provider', 'description',
            'configuration', 'is_active', 'is_connected', 'last_sync_at',
            'sync_frequency', 'metadata', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'organization', 'is_connected', 'last_sync_at', 'created_at', 'updated_at']

    def validate_provider(self, value):
        """Validate provider is supported."""
        valid_providers = [choice[0] for choice in Connector.PROVIDER_CHOICES]
        if value not in valid_providers:
            raise serializers.ValidationError(f'Invalid provider. Must be one of: {", ".join(valid_providers)}')
        return value

    def validate_sync_frequency(self, value):
        """Validate sync frequency format (cron expression or interval)."""
        if value and not isinstance(value, str):
            raise serializers.ValidationError('Sync frequency must be a string (cron expression or interval).')
        return value


class ConnectorCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a new connector."""

    class Meta:
        model = Connector
        fields = [
            'name', 'provider', 'description', 'configuration', 'sync_frequency'
        ]

    def create(self, validated_data):
        """Create connector with organization context."""
        organization = self.context['request'].organization
        if not organization:
            raise serializers.ValidationError('Organization context is required.')

        validated_data['organization'] = organization
        return super().create(validated_data)


class ConnectorCredentialSerializer(serializers.ModelSerializer):
    """Serializer for ConnectorCredential model."""

    connector_name = serializers.CharField(source='connector.name', read_only=True)

    class Meta:
        model = ConnectorCredential
        fields = [
            'id', 'connector', 'connector_name', 'credential_type',
            'expires_at', 'scopes', 'is_valid', 'last_validated_at',
            'metadata', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'is_valid', 'last_validated_at', 'created_at', 'updated_at'
        ]

    def to_representation(self, instance):
        """Hide encrypted credentials in response."""
        data = super().to_representation(instance)
        # Never expose actual credentials in API responses
        return data


class ConnectorWebhookSerializer(serializers.ModelSerializer):
    """Serializer for ConnectorWebhook model."""

    connector_name = serializers.CharField(source='connector.name', read_only=True)
    webhook_url_display = serializers.SerializerMethodField()

    class Meta:
        model = ConnectorWebhook
        fields = [
            'id', 'connector', 'connector_name', 'event_type',
            'webhook_url', 'webhook_url_display', 'webhook_secret',
            'is_active', 'is_verified', 'last_triggered_at',
            'metadata', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'webhook_url', 'webhook_secret', 'is_verified',
            'last_triggered_at', 'created_at', 'updated_at'
        ]

    def get_webhook_url_display(self, obj):
        """Return webhook URL for display."""
        if obj.webhook_url:
            return obj.webhook_url
        # Generate webhook URL based on connector and event type
        from django.conf import settings
        base_url = settings.BACKEND_URL or 'https://api.flowpilot.ai'
        return f'{base_url}/api/v1/connectors/webhooks/{obj.id}/'


class ConnectorSyncLogSerializer(serializers.ModelSerializer):
    """Serializer for ConnectorSyncLog model."""

    connector_name = serializers.CharField(source='connector.name', read_only=True)
    duration_seconds = serializers.SerializerMethodField()

    class Meta:
        model = ConnectorSyncLog
        fields = [
            'id', 'connector', 'connector_name', 'sync_type', 'status',
            'started_at', 'completed_at', 'duration_seconds',
            'records_synced', 'records_failed', 'error_message',
            'metadata', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

    def get_duration_seconds(self, obj):
        """Calculate sync duration in seconds."""
        if obj.started_at and obj.completed_at:
            delta = obj.completed_at - obj.started_at
            return delta.total_seconds()
        return None


class ConnectorOAuthInitiateSerializer(serializers.Serializer):
    """Serializer for initiating OAuth flow."""

    provider = serializers.ChoiceField(choices=[choice[0] for choice in Connector.PROVIDER_CHOICES])
    redirect_uri = serializers.URLField(
        required=False,
        help_text='Redirect URI after OAuth authorization (optional, uses default if not provided)'
    )
    scopes = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        help_text='List of OAuth scopes to request'
    )


class ConnectorOAuthCallbackSerializer(serializers.Serializer):
    """Serializer for OAuth callback."""

    code = serializers.CharField(help_text='OAuth authorization code')
    state = serializers.CharField(help_text='State parameter for CSRF protection')


class ConnectorTestSerializer(serializers.Serializer):
    """Serializer for testing connector connection."""

    test_type = serializers.ChoiceField(
        choices=['connection', 'authentication', 'list', 'fetch'],
        default='connection',
        help_text='Type of test to perform'
    )
    test_parameters = serializers.JSONField(
        required=False,
        help_text='Additional parameters for the test'
    )
