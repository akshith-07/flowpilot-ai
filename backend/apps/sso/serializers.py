"""
SSO serializers for API endpoints.
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model

from .models import (
    SSOProvider, SSOConnection, SSOSession,
    SSOAuditLog, SSOStateToken
)

User = get_user_model()


class SSOProviderSerializer(serializers.ModelSerializer):
    """Serializer for SSO provider."""

    class Meta:
        model = SSOProvider
        fields = [
            'id', 'name', 'provider_type', 'provider_name',
            'display_name', 'description', 'logo_url',
            'is_enabled', 'is_default', 'requires_email_verification',
            'authorization_url', 'token_url', 'userinfo_url', 'jwks_url',
            'sso_url', 'slo_url', 'entity_id',
            'scopes', 'metadata',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class SSOProviderListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing SSO providers."""

    class Meta:
        model = SSOProvider
        fields = [
            'id', 'name', 'provider_type', 'provider_name',
            'display_name', 'description', 'logo_url',
            'is_enabled'
        ]
        read_only_fields = ['id']


class SSOConnectionSerializer(serializers.ModelSerializer):
    """Serializer for SSO connection."""

    provider_details = SSOProviderListSerializer(source='provider', read_only=True)
    organization_name = serializers.CharField(source='organization.name', read_only=True)

    class Meta:
        model = SSOConnection
        fields = [
            'id', 'organization', 'provider', 'provider_details',
            'organization_name', 'name', 'status', 'is_default',
            'client_id', 'redirect_uri',
            'sp_entity_id', 'acs_url', 'idp_metadata_url',
            'auto_provision_users', 'auto_activate_users',
            'require_email_verification',
            'attribute_mapping', 'role_mapping', 'allowed_domains',
            'enforce_sso', 'pkce_required',
            'metadata', 'last_sync_at', 'last_error',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at', 'last_sync_at',
            'last_error', 'provider_details', 'organization_name'
        ]
        extra_kwargs = {
            'client_secret_encrypted': {'write_only': True},
            'idp_metadata_xml': {'write_only': True},
            'idp_certificate': {'write_only': True}
        }

    def validate_allowed_domains(self, value):
        """Validate allowed domains."""
        if not isinstance(value, list):
            raise serializers.ValidationError('allowed_domains must be a list')

        for domain in value:
            if not isinstance(domain, str) or '@' in domain:
                raise serializers.ValidationError('Invalid domain format')

        return value

    def validate_attribute_mapping(self, value):
        """Validate attribute mapping."""
        if not isinstance(value, dict):
            raise serializers.ValidationError('attribute_mapping must be a dictionary')

        return value

    def validate_role_mapping(self, value):
        """Validate role mapping."""
        if not isinstance(value, dict):
            raise serializers.ValidationError('role_mapping must be a dictionary')

        return value


class SSOConnectionCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating SSO connection."""

    client_secret = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = SSOConnection
        fields = [
            'organization', 'provider', 'name',
            'client_id', 'client_secret', 'redirect_uri',
            'sp_entity_id', 'acs_url', 'idp_metadata_url',
            'idp_metadata_xml', 'idp_certificate',
            'auto_provision_users', 'auto_activate_users',
            'require_email_verification',
            'attribute_mapping', 'role_mapping', 'allowed_domains',
            'enforce_sso', 'pkce_required'
        ]

    def create(self, validated_data):
        """Create SSO connection with encrypted client secret."""
        client_secret = validated_data.pop('client_secret', None)
        connection = SSOConnection(**validated_data)

        if client_secret:
            connection.client_secret_encrypted = client_secret

        connection.created_by = self.context['request'].user
        connection.save()

        return connection


class SSOConnectionUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating SSO connection."""

    client_secret = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = SSOConnection
        fields = [
            'name', 'status', 'is_default',
            'client_id', 'client_secret', 'redirect_uri',
            'sp_entity_id', 'acs_url', 'idp_metadata_url',
            'idp_metadata_xml', 'idp_certificate',
            'auto_provision_users', 'auto_activate_users',
            'require_email_verification',
            'attribute_mapping', 'role_mapping', 'allowed_domains',
            'enforce_sso', 'pkce_required'
        ]

    def update(self, instance, validated_data):
        """Update SSO connection with encrypted client secret."""
        client_secret = validated_data.pop('client_secret', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if client_secret:
            instance.client_secret_encrypted = client_secret

        instance.save()
        return instance


class SSOSessionSerializer(serializers.ModelSerializer):
    """Serializer for SSO session."""

    user_email = serializers.EmailField(source='user.email', read_only=True)
    provider_name = serializers.CharField(source='connection.provider.display_name', read_only=True)

    class Meta:
        model = SSOSession
        fields = [
            'id', 'user', 'user_email', 'connection', 'provider_name',
            'session_id', 'idp_session_id',
            'ip_address', 'user_agent',
            'access_token_expires_at', 'refresh_token_expires_at',
            'is_active', 'expires_at', 'last_activity',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'session_id', 'created_at', 'updated_at',
            'user_email', 'provider_name'
        ]


class SSOAuditLogSerializer(serializers.ModelSerializer):
    """Serializer for SSO audit log."""

    user_email = serializers.EmailField(source='user.email', read_only=True)
    connection_name = serializers.CharField(source='connection.name', read_only=True)

    class Meta:
        model = SSOAuditLog
        fields = [
            'id', 'event_type', 'severity', 'message',
            'user', 'user_email', 'connection', 'connection_name',
            'session', 'organization', 'email',
            'ip_address', 'user_agent', 'request_id',
            'provider_name', 'error_code', 'error_details', 'metadata',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'user_email', 'connection_name']


class SSOInitiateLoginSerializer(serializers.Serializer):
    """Serializer for initiating SSO login."""

    connection_id = serializers.UUIDField(required=True)
    redirect_uri = serializers.URLField(required=True)

    def validate_connection_id(self, value):
        """Validate connection exists and is active."""
        try:
            connection = SSOConnection.objects.get(id=value)
            if connection.status != 'active':
                raise serializers.ValidationError('SSO connection is not active')
            return value
        except SSOConnection.DoesNotExist:
            raise serializers.ValidationError('SSO connection not found')


class SSOCallbackSerializer(serializers.Serializer):
    """Serializer for SSO callback."""

    code = serializers.CharField(required=False)
    state = serializers.CharField(required=False)
    error = serializers.CharField(required=False)
    error_description = serializers.CharField(required=False)
    saml_response = serializers.CharField(required=False)

    def validate(self, data):
        """Validate callback data."""
        if data.get('error'):
            raise serializers.ValidationError({
                'error': data.get('error'),
                'error_description': data.get('error_description', 'Unknown error')
            })

        if not data.get('code') and not data.get('saml_response'):
            raise serializers.ValidationError('Missing authorization code or SAML response')

        return data


class SSOTestConnectionSerializer(serializers.Serializer):
    """Serializer for testing SSO connection."""

    connection_id = serializers.UUIDField(required=True)

    def validate_connection_id(self, value):
        """Validate connection exists."""
        try:
            SSOConnection.objects.get(id=value)
            return value
        except SSOConnection.DoesNotExist:
            raise serializers.ValidationError('SSO connection not found')


class SAMLMetadataSerializer(serializers.Serializer):
    """Serializer for SAML metadata."""

    connection_id = serializers.UUIDField(required=True)

    def validate_connection_id(self, value):
        """Validate connection exists and is SAML."""
        try:
            connection = SSOConnection.objects.get(id=value)
            if connection.provider.provider_type != 'saml2':
                raise serializers.ValidationError('Connection is not SAML 2.0')
            return value
        except SSOConnection.DoesNotExist:
            raise serializers.ValidationError('SSO connection not found')


class SSOProviderConfigSerializer(serializers.Serializer):
    """Serializer for SSO provider configuration (Google, Microsoft, etc.)."""

    provider_name = serializers.ChoiceField(
        choices=['google', 'microsoft', 'okta', 'onelogin', 'auth0']
    )
    client_id = serializers.CharField(required=True)
    client_secret = serializers.CharField(required=True, write_only=True)
    redirect_uri = serializers.URLField(required=True)
    allowed_domains = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        default=list
    )


class SSOConnectionStatsSerializer(serializers.Serializer):
    """Serializer for SSO connection statistics."""

    total_logins = serializers.IntegerField(read_only=True)
    successful_logins = serializers.IntegerField(read_only=True)
    failed_logins = serializers.IntegerField(read_only=True)
    active_sessions = serializers.IntegerField(read_only=True)
    unique_users = serializers.IntegerField(read_only=True)
    last_login_at = serializers.DateTimeField(read_only=True)
