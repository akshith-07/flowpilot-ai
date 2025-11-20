"""
Serializers for Users app.
"""
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from .models import User, UserSession, MFADevice, OAuthConnection
from core.utils import get_client_ip, get_user_agent
import pyotp


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model."""
    full_name = serializers.ReadOnlyField()
    is_mfa_enabled = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'full_name',
            'phone_number', 'phone_verified', 'avatar_url', 'timezone',
            'locale', 'is_active', 'email_verified', 'is_mfa_enabled',
            'last_login', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'email_verified', 'phone_verified', 'is_active', 'last_login', 'created_at', 'updated_at']


class UserRegistrationSerializer(serializers.Serializer):
    """Serializer for user registration."""
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100)
    timezone = serializers.CharField(max_length=50, default='UTC')
    locale = serializers.CharField(max_length=10, default='en')

    def validate_email(self, value):
        """Validate email is unique."""
        if User.objects.filter(email=value.lower()).exists():
            raise serializers.ValidationError('A user with this email already exists.')
        return value.lower()

    def validate_password(self, value):
        """Validate password strength."""
        try:
            validate_password(value)
        except DjangoValidationError as e:
            raise serializers.ValidationError(list(e.messages))
        return value

    def create(self, validated_data):
        """Create new user."""
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            timezone=validated_data.get('timezone', 'UTC'),
            locale=validated_data.get('locale', 'en'),
        )
        return user


class LoginSerializer(serializers.Serializer):
    """Serializer for user login."""
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    mfa_code = serializers.CharField(max_length=6, required=False, allow_blank=True)


class PasswordChangeSerializer(serializers.Serializer):
    """Serializer for password change."""
    old_password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    new_password = serializers.CharField(write_only=True, style={'input_type': 'password'})

    def validate_new_password(self, value):
        """Validate new password strength."""
        try:
            validate_password(value)
        except DjangoValidationError as e:
            raise serializers.ValidationError(list(e.messages))
        return value


class PasswordResetRequestSerializer(serializers.Serializer):
    """Serializer for password reset request."""
    email = serializers.EmailField()


class PasswordResetConfirmSerializer(serializers.Serializer):
    """Serializer for password reset confirmation."""
    token = serializers.CharField()
    new_password = serializers.CharField(write_only=True, style={'input_type': 'password'})

    def validate_new_password(self, value):
        """Validate new password strength."""
        try:
            validate_password(value)
        except DjangoValidationError as e:
            raise serializers.ValidationError(list(e.messages))
        return value


class UserSessionSerializer(serializers.ModelSerializer):
    """Serializer for UserSession model."""

    class Meta:
        model = UserSession
        fields = [
            'id', 'device_name', 'device_type', 'browser', 'os',
            'ip_address', 'is_active', 'last_activity', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class MFADeviceSerializer(serializers.ModelSerializer):
    """Serializer for MFADevice model."""
    qr_code_uri = serializers.SerializerMethodField()

    class Meta:
        model = MFADevice
        fields = [
            'id', 'device_name', 'device_type', 'is_active',
            'is_verified', 'verified_at', 'last_used_at',
            'created_at', 'qr_code_uri'
        ]
        read_only_fields = ['id', 'is_verified', 'verified_at', 'last_used_at', 'created_at']

    def get_qr_code_uri(self, obj):
        """Get QR code provisioning URI."""
        if obj.device_type == 'totp' and not obj.is_verified:
            return obj.get_provisioning_uri()
        return None


class MFASetupSerializer(serializers.Serializer):
    """Serializer for MFA setup."""
    device_name = serializers.CharField(max_length=100, default='Authenticator App')
    device_type = serializers.ChoiceField(choices=['totp'], default='totp')


class MFAVerifySerializer(serializers.Serializer):
    """Serializer for MFA verification."""
    device_id = serializers.UUIDField()
    code = serializers.CharField(max_length=6)


class MFADisableSerializer(serializers.Serializer):
    """Serializer for MFA disable."""
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})


class OAuthConnectionSerializer(serializers.ModelSerializer):
    """Serializer for OAuthConnection model."""

    class Meta:
        model = OAuthConnection
        fields = [
            'id', 'provider', 'email', 'scopes',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
