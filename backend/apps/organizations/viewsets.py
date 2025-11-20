"""
ViewSets for Organization models.
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db import transaction
from django.utils import timezone
from django.shortcuts import get_object_or_404

from .models import (
    Organization, OrganizationMember, Role, Invitation,
    Department, UsageQuota
)
from .serializers import (
    OrganizationSerializer, OrganizationListSerializer,
    OrganizationMemberSerializer, OrganizationMemberListSerializer,
    RoleSerializer, InvitationSerializer, DepartmentSerializer,
    UsageQuotaSerializer, AcceptInvitationSerializer
)
from .permissions import (
    IsOrganizationOwnerOrAdmin, IsOrganizationMember,
    CanManageMembers, CanManageRoles
)
from .services import OrganizationService


class OrganizationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Organization model.

    list: Get all organizations for current user
    create: Create a new organization
    retrieve: Get organization details
    update: Update organization
    partial_update: Partially update organization
    destroy: Delete organization
    """
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'slug', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['-created_at']
    filterset_fields = ['is_active']

    def get_queryset(self):
        """Get organizations where user is a member."""
        user = self.request.user
        return Organization.objects.filter(
            members__user=user,
            members__is_active=True
        ).distinct().select_related('owner').prefetch_related('members')

    def get_serializer_class(self):
        """Return appropriate serializer class."""
        if self.action == 'list':
            return OrganizationListSerializer
        return OrganizationSerializer

    def get_permissions(self):
        """Get permissions based on action."""
        if self.action in ['update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsOrganizationOwnerOrAdmin()]
        return super().get_permissions()

    @transaction.atomic
    def perform_create(self, serializer):
        """Create organization and add creator as owner."""
        organization = serializer.save(owner=self.request.user)

        # Create default roles
        OrganizationService.create_default_roles(organization)

        # Add creator as owner member
        owner_role = organization.roles.get(role_type='owner')
        OrganizationMember.objects.create(
            organization=organization,
            user=self.request.user,
            role=owner_role,
            is_active=True
        )

        # Create default quotas
        OrganizationService.create_default_quotas(organization)

    @action(detail=True, methods=['get'])
    def members(self, request, pk=None):
        """Get all members of the organization."""
        organization = self.get_object()
        members = organization.members.filter(is_active=True).select_related(
            'user', 'role', 'department'
        )

        serializer = OrganizationMemberListSerializer(members, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def statistics(self, request, pk=None):
        """Get organization statistics."""
        organization = self.get_object()
        stats = OrganizationService.get_organization_statistics(organization)
        return Response(stats)

    @action(detail=True, methods=['post'])
    def switch(self, request, pk=None):
        """Switch current organization context."""
        organization = self.get_object()

        # Verify user is a member
        if not organization.members.filter(
            user=request.user,
            is_active=True
        ).exists():
            return Response(
                {'error': 'You are not a member of this organization'},
                status=status.HTTP_403_FORBIDDEN
            )

        # Store in session or return organization data
        return Response({
            'message': 'Organization switched successfully',
            'organization': OrganizationSerializer(organization).data
        })


class OrganizationMemberViewSet(viewsets.ModelViewSet):
    """
    ViewSet for OrganizationMember model.

    list: Get all members
    create: Add a new member
    retrieve: Get member details
    update: Update member
    partial_update: Partially update member
    destroy: Remove member
    """
    permission_classes = [IsAuthenticated, IsOrganizationMember]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['user__email', 'user__first_name', 'user__last_name', 'title']
    ordering_fields = ['joined_at', 'user__email']
    ordering = ['-joined_at']
    filterset_fields = ['is_active', 'role', 'department']

    def get_queryset(self):
        """Get members based on organization context."""
        organization_id = self.request.query_params.get('organization')
        if not organization_id:
            return OrganizationMember.objects.none()

        return OrganizationMember.objects.filter(
            organization_id=organization_id
        ).select_related('user', 'role', 'department')

    def get_serializer_class(self):
        """Return appropriate serializer class."""
        if self.action == 'list':
            return OrganizationMemberListSerializer
        return OrganizationMemberSerializer

    def get_permissions(self):
        """Get permissions based on action."""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), CanManageMembers()]
        return super().get_permissions()

    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """Deactivate a member."""
        member = self.get_object()
        member.is_active = False
        member.save()

        return Response({
            'message': 'Member deactivated successfully'
        })

    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """Activate a member."""
        member = self.get_object()
        member.is_active = True
        member.save()

        return Response({
            'message': 'Member activated successfully'
        })

    @action(detail=True, methods=['post'])
    def change_role(self, request, pk=None):
        """Change member's role."""
        member = self.get_object()
        role_id = request.data.get('role')

        if not role_id:
            return Response(
                {'error': 'Role ID is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        role = get_object_or_404(
            Role,
            id=role_id,
            organization=member.organization
        )

        member.role = role
        member.save()

        return Response({
            'message': 'Role changed successfully',
            'member': OrganizationMemberSerializer(member).data
        })


class RoleViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Role model.

    list: Get all roles
    create: Create a new role
    retrieve: Get role details
    update: Update role
    partial_update: Partially update role
    destroy: Delete role
    """
    permission_classes = [IsAuthenticated, IsOrganizationMember]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']
    filterset_fields = ['is_active', 'role_type']

    def get_queryset(self):
        """Get roles based on organization context."""
        organization_id = self.request.query_params.get('organization')
        if not organization_id:
            return Role.objects.none()

        return Role.objects.filter(
            organization_id=organization_id
        ).prefetch_related('members')

    def get_serializer_class(self):
        """Return serializer class."""
        return RoleSerializer

    def get_permissions(self):
        """Get permissions based on action."""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), CanManageRoles()]
        return super().get_permissions()

    def perform_destroy(self, instance):
        """Prevent deletion of system roles."""
        if instance.is_system_role:
            raise serializers.ValidationError('System roles cannot be deleted.')

        # Check if role has members
        if instance.members.filter(is_active=True).exists():
            raise serializers.ValidationError(
                'Cannot delete role with active members. Please reassign members first.'
            )

        super().perform_destroy(instance)


class DepartmentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Department model.

    list: Get all departments
    create: Create a new department
    retrieve: Get department details
    update: Update department
    partial_update: Partially update department
    destroy: Delete department
    """
    permission_classes = [IsAuthenticated, IsOrganizationMember]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']
    filterset_fields = ['is_active', 'parent']

    def get_queryset(self):
        """Get departments based on organization context."""
        organization_id = self.request.query_params.get('organization')
        if not organization_id:
            return Department.objects.none()

        return Department.objects.filter(
            organization_id=organization_id
        ).select_related('manager', 'parent')

    def get_serializer_class(self):
        """Return serializer class."""
        return DepartmentSerializer

    def get_permissions(self):
        """Get permissions based on action."""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsOrganizationOwnerOrAdmin()]
        return super().get_permissions()

    @action(detail=True, methods=['get'])
    def members(self, request, pk=None):
        """Get all members in this department."""
        department = self.get_object()
        members = department.members.filter(is_active=True).select_related('user', 'role')

        serializer = OrganizationMemberListSerializer(members, many=True)
        return Response(serializer.data)


class InvitationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Invitation model.

    list: Get all invitations
    create: Send a new invitation
    retrieve: Get invitation details
    update: Update invitation
    destroy: Revoke invitation
    """
    permission_classes = [IsAuthenticated, IsOrganizationMember]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['email']
    ordering_fields = ['created_at', 'expires_at']
    ordering = ['-created_at']
    filterset_fields = ['status', 'organization']

    def get_queryset(self):
        """Get invitations based on organization context."""
        organization_id = self.request.query_params.get('organization')
        if not organization_id:
            return Invitation.objects.none()

        return Invitation.objects.filter(
            organization_id=organization_id
        ).select_related('organization', 'role', 'invited_by')

    def get_serializer_class(self):
        """Return serializer class."""
        return InvitationSerializer

    def get_permissions(self):
        """Get permissions based on action."""
        if self.action in ['create', 'destroy']:
            return [IsAuthenticated(), CanManageMembers()]
        if self.action in ['accept']:
            return [IsAuthenticated()]
        return super().get_permissions()

    @transaction.atomic
    def perform_create(self, serializer):
        """Create invitation and send email."""
        invitation = serializer.save()

        # Send invitation email (implement in tasks)
        from .tasks import send_invitation_email
        send_invitation_email.delay(invitation.id)

    @action(detail=False, methods=['post'])
    def accept(self, request):
        """Accept an invitation."""
        serializer = AcceptInvitationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        token = serializer.validated_data['token']
        invitation = Invitation.objects.get(token=token)

        # Check if user email matches invitation
        if request.user.email != invitation.email:
            return Response(
                {'error': 'This invitation is for a different email address'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create organization member
        with transaction.atomic():
            OrganizationMember.objects.create(
                organization=invitation.organization,
                user=request.user,
                role=invitation.role,
                is_active=True
            )

            # Update invitation status
            invitation.status = 'accepted'
            invitation.accepted_at = timezone.now()
            invitation.save()

        return Response({
            'message': 'Invitation accepted successfully',
            'organization': OrganizationSerializer(invitation.organization).data
        })

    @action(detail=True, methods=['post'])
    def resend(self, request, pk=None):
        """Resend an invitation email."""
        invitation = self.get_object()

        if invitation.status != 'pending':
            return Response(
                {'error': 'Can only resend pending invitations'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if invitation.is_expired():
            # Extend expiry
            invitation.expires_at = timezone.now() + timezone.timedelta(days=7)
            invitation.save()

        # Send email
        from .tasks import send_invitation_email
        send_invitation_email.delay(invitation.id)

        return Response({
            'message': 'Invitation resent successfully'
        })

    @action(detail=True, methods=['post'])
    def revoke(self, request, pk=None):
        """Revoke an invitation."""
        invitation = self.get_object()

        if invitation.status != 'pending':
            return Response(
                {'error': 'Can only revoke pending invitations'},
                status=status.HTTP_400_BAD_REQUEST
            )

        invitation.status = 'revoked'
        invitation.save()

        return Response({
            'message': 'Invitation revoked successfully'
        })


class UsageQuotaViewSet(viewsets.ModelViewSet):
    """
    ViewSet for UsageQuota model.

    list: Get all quotas
    create: Create a new quota
    retrieve: Get quota details
    update: Update quota
    partial_update: Partially update quota
    destroy: Delete quota
    """
    permission_classes = [IsAuthenticated, IsOrganizationMember]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    ordering_fields = ['quota_type', 'created_at']
    ordering = ['quota_type']
    filterset_fields = ['is_active', 'quota_type', 'period']

    def get_queryset(self):
        """Get quotas based on organization context."""
        organization_id = self.request.query_params.get('organization')
        if not organization_id:
            return UsageQuota.objects.none()

        return UsageQuota.objects.filter(
            organization_id=organization_id
        )

    def get_serializer_class(self):
        """Return serializer class."""
        return UsageQuotaSerializer

    def get_permissions(self):
        """Get permissions based on action."""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsOrganizationOwnerOrAdmin()]
        return super().get_permissions()

    @action(detail=True, methods=['post'])
    def reset(self, request, pk=None):
        """Reset quota usage."""
        quota = self.get_object()
        quota.reset_usage()

        return Response({
            'message': 'Quota reset successfully',
            'quota': UsageQuotaSerializer(quota).data
        })

    @action(detail=True, methods=['post'])
    def increment(self, request, pk=None):
        """Increment quota usage."""
        quota = self.get_object()
        amount = request.data.get('amount', 1)

        try:
            quota.increment_usage(amount)
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response({
            'message': 'Quota incremented successfully',
            'quota': UsageQuotaSerializer(quota).data
        })
