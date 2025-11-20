"""
Custom permissions for SSO app.
"""
from rest_framework import permissions


class IsSSOAdmin(permissions.BasePermission):
    """
    Permission for SSO administrators.
    Only organization owners/admins can manage SSO connections.
    """

    def has_permission(self, request, view):
        """Check if user is authenticated."""
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        """Check if user is admin of the organization."""
        if request.user.is_superuser:
            return True

        # Check if user is owner/admin of organization
        if hasattr(obj, 'organization'):
            return obj.organization.members.filter(
                user=request.user,
                role__name__in=['Owner', 'Admin']
            ).exists()

        return False


class CanManageSSOConnection(permissions.BasePermission):
    """
    Permission to manage SSO connections.
    """

    def has_object_permission(self, request, view, obj):
        """Check if user can manage this SSO connection."""
        if request.user.is_superuser:
            return True

        # Read-only for all authenticated users
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions only for org admins
        return obj.organization.members.filter(
            user=request.user,
            role__name__in=['Owner', 'Admin']
        ).exists()
