"""
Filters for Organizations app.
"""
from django_filters import rest_framework as filters
from .models import (
    Organization, OrganizationMember, Role, Invitation,
    Department, UsageQuota
)


class OrganizationFilter(filters.FilterSet):
    """Filter for Organization model."""

    name = filters.CharFilter(lookup_expr='icontains')
    created_after = filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_before = filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')

    class Meta:
        model = Organization
        fields = ['is_active', 'name']


class OrganizationMemberFilter(filters.FilterSet):
    """Filter for OrganizationMember model."""

    user_email = filters.CharFilter(field_name='user__email', lookup_expr='icontains')
    joined_after = filters.DateTimeFilter(field_name='joined_at', lookup_expr='gte')
    joined_before = filters.DateTimeFilter(field_name='joined_at', lookup_expr='lte')

    class Meta:
        model = OrganizationMember
        fields = ['is_active', 'role', 'department', 'organization']


class RoleFilter(filters.FilterSet):
    """Filter for Role model."""

    name = filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Role
        fields = ['is_active', 'role_type', 'organization']


class InvitationFilter(filters.FilterSet):
    """Filter for Invitation model."""

    email = filters.CharFilter(lookup_expr='icontains')
    created_after = filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_before = filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    expires_after = filters.DateTimeFilter(field_name='expires_at', lookup_expr='gte')
    expires_before = filters.DateTimeFilter(field_name='expires_at', lookup_expr='lte')

    class Meta:
        model = Invitation
        fields = ['status', 'organization']


class DepartmentFilter(filters.FilterSet):
    """Filter for Department model."""

    name = filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Department
        fields = ['is_active', 'organization', 'parent']


class UsageQuotaFilter(filters.FilterSet):
    """Filter for UsageQuota model."""

    class Meta:
        model = UsageQuota
        fields = ['is_active', 'quota_type', 'period', 'organization']
