"""
Business logic services for Organizations app.
"""
from django.db.models import Count, Q
from django.utils import timezone
from .models import Organization, Role, UsageQuota


class OrganizationService:
    """Service class for organization-related business logic."""

    @staticmethod
    def create_default_roles(organization):
        """
        Create default roles for a new organization.

        Args:
            organization: Organization instance

        Returns:
            dict: Created roles
        """
        roles = {
            'owner': {
                'name': 'Owner',
                'role_type': 'owner',
                'description': 'Full access to all organization features',
                'is_system_role': True,
                'permissions': {
                    'workflows': {'create': True, 'read': True, 'update': True, 'delete': True},
                    'executions': {'create': True, 'read': True, 'update': True, 'delete': True},
                    'documents': {'create': True, 'read': True, 'update': True, 'delete': True},
                    'connectors': {'create': True, 'read': True, 'update': True, 'delete': True},
                    'analytics': {'create': True, 'read': True, 'update': True, 'delete': True},
                    'members': {'create': True, 'read': True, 'update': True, 'delete': True},
                    'settings': {'create': True, 'read': True, 'update': True, 'delete': True},
                    'billing': {'create': True, 'read': True, 'update': True, 'delete': True},
                }
            },
            'admin': {
                'name': 'Administrator',
                'role_type': 'admin',
                'description': 'Administrative access to most features',
                'is_system_role': True,
                'permissions': {
                    'workflows': {'create': True, 'read': True, 'update': True, 'delete': True},
                    'executions': {'create': True, 'read': True, 'update': True, 'delete': True},
                    'documents': {'create': True, 'read': True, 'update': True, 'delete': True},
                    'connectors': {'create': True, 'read': True, 'update': True, 'delete': True},
                    'analytics': {'create': True, 'read': True, 'update': True, 'delete': True},
                    'members': {'create': True, 'read': True, 'update': True, 'delete': False},
                    'settings': {'create': False, 'read': True, 'update': True, 'delete': False},
                    'billing': {'create': False, 'read': True, 'update': False, 'delete': False},
                }
            },
            'manager': {
                'name': 'Manager',
                'role_type': 'manager',
                'description': 'Can manage workflows and view analytics',
                'is_system_role': True,
                'permissions': {
                    'workflows': {'create': True, 'read': True, 'update': True, 'delete': True},
                    'executions': {'create': True, 'read': True, 'update': True, 'delete': False},
                    'documents': {'create': True, 'read': True, 'update': True, 'delete': True},
                    'connectors': {'create': False, 'read': True, 'update': False, 'delete': False},
                    'analytics': {'create': False, 'read': True, 'update': False, 'delete': False},
                    'members': {'create': False, 'read': True, 'update': False, 'delete': False},
                    'settings': {'create': False, 'read': True, 'update': False, 'delete': False},
                    'billing': {'create': False, 'read': True, 'update': False, 'delete': False},
                }
            },
            'member': {
                'name': 'Member',
                'role_type': 'member',
                'description': 'Can create and manage own workflows',
                'is_system_role': True,
                'permissions': {
                    'workflows': {'create': True, 'read': True, 'update': True, 'delete': False},
                    'executions': {'create': True, 'read': True, 'update': False, 'delete': False},
                    'documents': {'create': True, 'read': True, 'update': True, 'delete': False},
                    'connectors': {'create': False, 'read': True, 'update': False, 'delete': False},
                    'analytics': {'create': False, 'read': True, 'update': False, 'delete': False},
                    'members': {'create': False, 'read': True, 'update': False, 'delete': False},
                    'settings': {'create': False, 'read': True, 'update': False, 'delete': False},
                    'billing': {'create': False, 'read': False, 'update': False, 'delete': False},
                }
            },
            'viewer': {
                'name': 'Viewer',
                'role_type': 'viewer',
                'description': 'Read-only access',
                'is_system_role': True,
                'permissions': {
                    'workflows': {'create': False, 'read': True, 'update': False, 'delete': False},
                    'executions': {'create': False, 'read': True, 'update': False, 'delete': False},
                    'documents': {'create': False, 'read': True, 'update': False, 'delete': False},
                    'connectors': {'create': False, 'read': True, 'update': False, 'delete': False},
                    'analytics': {'create': False, 'read': True, 'update': False, 'delete': False},
                    'members': {'create': False, 'read': True, 'update': False, 'delete': False},
                    'settings': {'create': False, 'read': True, 'update': False, 'delete': False},
                    'billing': {'create': False, 'read': False, 'update': False, 'delete': False},
                }
            },
        }

        created_roles = {}
        for role_type, role_data in roles.items():
            role = Role.objects.create(
                organization=organization,
                **role_data
            )
            created_roles[role_type] = role

        return created_roles

    @staticmethod
    def create_default_quotas(organization):
        """
        Create default usage quotas for a new organization.

        Args:
            organization: Organization instance

        Returns:
            list: Created quotas
        """
        default_quotas = [
            {
                'quota_type': 'workflows',
                'period': 'total',
                'limit': 100,
            },
            {
                'quota_type': 'executions',
                'period': 'monthly',
                'limit': 10000,
            },
            {
                'quota_type': 'api_calls',
                'period': 'monthly',
                'limit': 100000,
            },
            {
                'quota_type': 'storage',
                'period': 'total',
                'limit': 10,  # 10 GB
            },
            {
                'quota_type': 'members',
                'period': 'total',
                'limit': 50,
            },
            {
                'quota_type': 'ai_tokens',
                'period': 'monthly',
                'limit': 1000000,  # 1M tokens
            },
            {
                'quota_type': 'documents',
                'period': 'monthly',
                'limit': 1000,
            },
        ]

        quotas = []
        for quota_data in default_quotas:
            quota = UsageQuota.objects.create(
                organization=organization,
                **quota_data
            )
            quotas.append(quota)

        return quotas

    @staticmethod
    def get_organization_statistics(organization):
        """
        Get comprehensive statistics for an organization.

        Args:
            organization: Organization instance

        Returns:
            dict: Statistics
        """
        from apps.workflows.models import Workflow
        from apps.executions.models import WorkflowExecution
        from apps.documents.models import Document

        stats = {
            'members': {
                'total': organization.members.filter(is_active=True).count(),
                'by_role': dict(
                    organization.members.filter(is_active=True)
                    .values('role__name')
                    .annotate(count=Count('id'))
                    .values_list('role__name', 'count')
                ),
            },
            'workflows': {
                'total': Workflow.objects.filter(organization=organization).count(),
                'active': Workflow.objects.filter(
                    organization=organization,
                    is_active=True
                ).count(),
            },
            'executions': {
                'total': WorkflowExecution.objects.filter(
                    workflow__organization=organization
                ).count(),
                'last_30_days': WorkflowExecution.objects.filter(
                    workflow__organization=organization,
                    created_at__gte=timezone.now() - timezone.timedelta(days=30)
                ).count(),
            },
            'documents': {
                'total': Document.objects.filter(organization=organization).count(),
                'last_30_days': Document.objects.filter(
                    organization=organization,
                    created_at__gte=timezone.now() - timezone.timedelta(days=30)
                ).count(),
            },
            'quotas': {
                quota.quota_type: {
                    'limit': quota.limit,
                    'current_usage': quota.current_usage,
                    'usage_percentage': quota.usage_percentage,
                    'is_exceeded': quota.is_quota_exceeded,
                }
                for quota in organization.quotas.filter(is_active=True)
            },
        }

        return stats

    @staticmethod
    def check_quota(organization, quota_type, amount=1):
        """
        Check if organization has quota available.

        Args:
            organization: Organization instance
            quota_type: Type of quota to check
            amount: Amount to check

        Returns:
            tuple: (has_quota: bool, quota: UsageQuota or None)

        Raises:
            ValueError: If quota is exceeded
        """
        try:
            quota = organization.quotas.get(
                quota_type=quota_type,
                is_active=True
            )

            if quota.is_enforced:
                if (quota.current_usage + amount) > quota.limit:
                    raise ValueError(
                        f'{quota_type} quota exceeded. '
                        f'Current: {quota.current_usage}, Limit: {quota.limit}'
                    )

            return True, quota

        except UsageQuota.DoesNotExist:
            # No quota defined, allow operation
            return True, None

    @staticmethod
    def increment_quota(organization, quota_type, amount=1):
        """
        Increment organization quota usage.

        Args:
            organization: Organization instance
            quota_type: Type of quota
            amount: Amount to increment

        Returns:
            UsageQuota or None
        """
        try:
            quota = organization.quotas.get(
                quota_type=quota_type,
                is_active=True
            )
            quota.increment_usage(amount)
            return quota

        except UsageQuota.DoesNotExist:
            return None

    @staticmethod
    def get_user_organizations(user):
        """
        Get all organizations for a user.

        Args:
            user: User instance

        Returns:
            QuerySet: Organizations
        """
        return Organization.objects.filter(
            members__user=user,
            members__is_active=True,
            is_active=True
        ).distinct().select_related('owner').prefetch_related('members')

    @staticmethod
    def get_user_role_in_organization(user, organization):
        """
        Get user's role in an organization.

        Args:
            user: User instance
            organization: Organization instance

        Returns:
            Role or None
        """
        try:
            member = organization.members.get(user=user, is_active=True)
            return member.role
        except:
            return None

    @staticmethod
    def user_has_permission(user, organization, module, action):
        """
        Check if user has specific permission in organization.

        Args:
            user: User instance
            organization: Organization instance
            module: Module name
            action: Action name

        Returns:
            bool: True if user has permission
        """
        try:
            member = organization.members.get(user=user, is_active=True)
            return member.has_permission(module, action)
        except:
            return False
