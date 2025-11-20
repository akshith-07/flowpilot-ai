"""
Custom permission classes for FlowPilot AI.
"""
from rest_framework import permissions


class IsOrganizationMember(permissions.BasePermission):
    """
    Permission to check if user is a member of the organization.
    """
    message = 'You must be a member of this organization.'

    def has_permission(self, request, view):
        """Check if user has organization membership."""
        return (
            request.user and
            request.user.is_authenticated and
            hasattr(request, 'organization') and
            request.organization is not None
        )


class IsOrganizationAdmin(permissions.BasePermission):
    """
    Permission to check if user is an admin of the organization.
    """
    message = 'You must be an admin of this organization.'

    def has_permission(self, request, view):
        """Check if user is organization admin."""
        if not (request.user and request.user.is_authenticated):
            return False

        if not hasattr(request, 'organization_member'):
            return False

        member = request.organization_member
        return member and member.role.slug in ['owner', 'admin']


class IsOrganizationOwner(permissions.BasePermission):
    """
    Permission to check if user is the owner of the organization.
    """
    message = 'You must be the owner of this organization.'

    def has_permission(self, request, view):
        """Check if user is organization owner."""
        if not (request.user and request.user.is_authenticated):
            return False

        if not hasattr(request, 'organization_member'):
            return False

        member = request.organization_member
        return member and member.role.slug == 'owner'


class HasResourcePermission(permissions.BasePermission):
    """
    Permission to check if user has specific resource permission.
    Usage: Add permission_required attribute to view.
    Example: permission_required = 'workflows:create'
    """
    message = 'You do not have permission to perform this action.'

    def has_permission(self, request, view):
        """Check if user has required permission."""
        if not (request.user and request.user.is_authenticated):
            return False

        if not hasattr(view, 'permission_required'):
            return True  # No specific permission required

        if not hasattr(request, 'organization_member'):
            return False

        member = request.organization_member
        if not member:
            return False

        # Parse permission (e.g., 'workflows:create')
        resource, action = view.permission_required.split(':')

        # Check role permissions
        permissions_dict = member.role.permissions
        resource_perms = permissions_dict.get(resource, {})

        return resource_perms.get(action, False)


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    Assumes the model instance has a 'created_by' or 'owner' attribute.
    """

    def has_object_permission(self, request, view, obj):
        """Check if user is the owner of the object."""
        # Read permissions are allowed for any request
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner
        owner = getattr(obj, 'created_by', None) or getattr(obj, 'owner', None)
        return owner == request.user
