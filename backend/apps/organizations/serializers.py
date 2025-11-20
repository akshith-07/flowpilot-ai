"""
Serializers for Organization models.
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import (
    Organization, OrganizationMember, Role, Invitation,
    Department, UsageQuota
)

User = get_user_model()


class OrganizationSerializer(serializers.ModelSerializer):
    """Serializer for Organization model."""

    member_count = serializers.ReadOnlyField()
    workflow_count = serializers.ReadOnlyField()
    owner_email = serializers.EmailField(source='owner.email', read_only=True)
    owner_name = serializers.CharField(source='owner.full_name', read_only=True)

    class Meta:
        model = Organization
        fields = [
            'id', 'name', 'slug', 'parent', 'description', 'website',
            'logo_url', 'email', 'phone', 'address_line1', 'address_line2',
            'city', 'state', 'country', 'postal_code', 'settings', 'metadata',
            'is_active', 'primary_color', 'timezone', 'locale', 'owner',
            'owner_email', 'owner_name', 'member_count', 'workflow_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'owner']

    def validate_slug(self, value):
        """Validate slug uniqueness."""
        if self.instance:
            # Update case - exclude current instance
            if Organization.objects.filter(slug=value).exclude(id=self.instance.id).exists():
                raise serializers.ValidationError('Organization with this slug already exists.')
        else:
            # Create case
            if Organization.objects.filter(slug=value).exists():
                raise serializers.ValidationError('Organization with this slug already exists.')
        return value

    def create(self, validated_data):
        """Create organization and set owner from request user."""
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['owner'] = request.user
        return super().create(validated_data)


class OrganizationListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for organization lists."""

    member_count = serializers.ReadOnlyField()
    owner_email = serializers.EmailField(source='owner.email', read_only=True)

    class Meta:
        model = Organization
        fields = [
            'id', 'name', 'slug', 'logo_url', 'is_active',
            'owner_email', 'member_count', 'created_at'
        ]
        read_only_fields = fields


class RoleSerializer(serializers.ModelSerializer):
    """Serializer for Role model."""

    member_count = serializers.SerializerMethodField()

    class Meta:
        model = Role
        fields = [
            'id', 'organization', 'name', 'role_type', 'description',
            'permissions', 'is_active', 'is_system_role', 'member_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_system_role']

    def get_member_count(self, obj):
        """Get count of members with this role."""
        return obj.members.filter(is_active=True).count()

    def validate_name(self, value):
        """Validate role name uniqueness within organization."""
        organization = self.initial_data.get('organization') or (
            self.instance.organization if self.instance else None
        )

        if not organization:
            return value

        query = Role.objects.filter(organization=organization, name=value)
        if self.instance:
            query = query.exclude(id=self.instance.id)

        if query.exists():
            raise serializers.ValidationError('Role with this name already exists in this organization.')

        return value

    def validate(self, attrs):
        """Validate role permissions structure."""
        permissions = attrs.get('permissions', {})

        if permissions:
            # Validate permissions structure
            valid_modules = [
                'workflows', 'executions', 'documents', 'connectors',
                'analytics', 'members', 'settings', 'billing'
            ]
            valid_actions = ['create', 'read', 'update', 'delete']

            for module, actions in permissions.items():
                if module not in valid_modules:
                    raise serializers.ValidationError(
                        f'Invalid module: {module}. Valid modules: {", ".join(valid_modules)}'
                    )

                if not isinstance(actions, dict):
                    raise serializers.ValidationError(
                        f'Permissions for {module} must be a dictionary'
                    )

                for action, value in actions.items():
                    if action not in valid_actions:
                        raise serializers.ValidationError(
                            f'Invalid action: {action}. Valid actions: {", ".join(valid_actions)}'
                        )
                    if not isinstance(value, bool):
                        raise serializers.ValidationError(
                            f'Permission value for {module}.{action} must be a boolean'
                        )

        return attrs


class DepartmentSerializer(serializers.ModelSerializer):
    """Serializer for Department model."""

    member_count = serializers.SerializerMethodField()
    manager_name = serializers.CharField(source='manager.full_name', read_only=True)

    class Meta:
        model = Department
        fields = [
            'id', 'organization', 'name', 'description', 'parent',
            'manager', 'manager_name', 'is_active', 'member_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_member_count(self, obj):
        """Get count of members in this department."""
        return obj.members.filter(is_active=True).count()


class OrganizationMemberSerializer(serializers.ModelSerializer):
    """Serializer for OrganizationMember model."""

    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_name = serializers.CharField(source='user.full_name', read_only=True)
    role_name = serializers.CharField(source='role.name', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)

    class Meta:
        model = OrganizationMember
        fields = [
            'id', 'organization', 'user', 'user_email', 'user_name',
            'role', 'role_name', 'department', 'department_name',
            'custom_permissions', 'is_active', 'title', 'metadata',
            'joined_at', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'joined_at', 'created_at', 'updated_at']

    def validate(self, attrs):
        """Validate organization member."""
        organization = attrs.get('organization')
        user = attrs.get('user')
        role = attrs.get('role')

        # Check if role belongs to the organization
        if role and organization and role.organization != organization:
            raise serializers.ValidationError('Role does not belong to this organization.')

        # Check for existing membership (on create)
        if not self.instance:
            if OrganizationMember.objects.filter(
                organization=organization,
                user=user
            ).exists():
                raise serializers.ValidationError('User is already a member of this organization.')

        return attrs


class OrganizationMemberListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for member lists."""

    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_name = serializers.CharField(source='user.full_name', read_only=True)
    role_name = serializers.CharField(source='role.name', read_only=True)

    class Meta:
        model = OrganizationMember
        fields = [
            'id', 'user_email', 'user_name', 'role_name',
            'title', 'is_active', 'joined_at'
        ]
        read_only_fields = fields


class InvitationSerializer(serializers.ModelSerializer):
    """Serializer for Invitation model."""

    invited_by_email = serializers.EmailField(source='invited_by.email', read_only=True)
    invited_by_name = serializers.CharField(source='invited_by.full_name', read_only=True)
    role_name = serializers.CharField(source='role.name', read_only=True)
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    is_expired = serializers.SerializerMethodField()
    is_valid = serializers.SerializerMethodField()

    class Meta:
        model = Invitation
        fields = [
            'id', 'organization', 'organization_name', 'email', 'role',
            'role_name', 'invited_by', 'invited_by_email', 'invited_by_name',
            'token', 'status', 'message', 'metadata', 'expires_at',
            'accepted_at', 'is_expired', 'is_valid', 'created_at'
        ]
        read_only_fields = [
            'id', 'token', 'status', 'accepted_at', 'created_at',
            'invited_by'
        ]

    def get_is_expired(self, obj):
        """Check if invitation is expired."""
        return obj.is_expired()

    def get_is_valid(self, obj):
        """Check if invitation is valid."""
        return obj.is_valid()

    def create(self, validated_data):
        """Create invitation with token and invited_by from request."""
        import secrets

        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['invited_by'] = request.user

        # Generate secure token
        validated_data['token'] = secrets.token_urlsafe(32)

        # Set expiry (7 days from now)
        validated_data['expires_at'] = timezone.now() + timezone.timedelta(days=7)

        return super().create(validated_data)

    def validate(self, attrs):
        """Validate invitation."""
        organization = attrs.get('organization')
        email = attrs.get('email')
        role = attrs.get('role')

        # Check if role belongs to organization
        if role and organization and role.organization != organization:
            raise serializers.ValidationError('Role does not belong to this organization.')

        # Check if user is already a member
        user = User.objects.filter(email=email).first()
        if user:
            if OrganizationMember.objects.filter(
                organization=organization,
                user=user,
                is_active=True
            ).exists():
                raise serializers.ValidationError('User is already a member of this organization.')

        # Check for existing pending invitation
        if Invitation.objects.filter(
            organization=organization,
            email=email,
            status='pending',
            expires_at__gt=timezone.now()
        ).exists():
            raise serializers.ValidationError('An active invitation already exists for this email.')

        return attrs


class UsageQuotaSerializer(serializers.ModelSerializer):
    """Serializer for UsageQuota model."""

    usage_percentage = serializers.ReadOnlyField()
    is_quota_exceeded = serializers.ReadOnlyField()
    is_warning_threshold_reached = serializers.ReadOnlyField()
    is_alert_threshold_reached = serializers.ReadOnlyField()

    class Meta:
        model = UsageQuota
        fields = [
            'id', 'organization', 'quota_type', 'period', 'limit',
            'current_usage', 'warning_threshold', 'alert_threshold',
            'is_active', 'is_enforced', 'period_start', 'period_end',
            'last_reset_at', 'usage_percentage', 'is_quota_exceeded',
            'is_warning_threshold_reached', 'is_alert_threshold_reached',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'current_usage', 'last_reset_at', 'created_at', 'updated_at'
        ]

    def validate(self, attrs):
        """Validate quota thresholds."""
        warning_threshold = attrs.get('warning_threshold', 80)
        alert_threshold = attrs.get('alert_threshold', 95)

        if warning_threshold >= alert_threshold:
            raise serializers.ValidationError(
                'Warning threshold must be less than alert threshold.'
            )

        if warning_threshold > 100 or alert_threshold > 100:
            raise serializers.ValidationError(
                'Thresholds must be between 0 and 100.'
            )

        return attrs


class AcceptInvitationSerializer(serializers.Serializer):
    """Serializer for accepting invitations."""

    token = serializers.CharField(required=True)

    def validate_token(self, value):
        """Validate invitation token."""
        try:
            invitation = Invitation.objects.get(token=value)
        except Invitation.DoesNotExist:
            raise serializers.ValidationError('Invalid invitation token.')

        if not invitation.is_valid():
            raise serializers.ValidationError('This invitation has expired or is no longer valid.')

        return value
