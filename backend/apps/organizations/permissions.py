"""
Custom permissions for Organizations app.
"""
from rest_framework import permissions


class IsOrganizationMember(permissions.BasePermission):
    """
    Permission to check if user is a member of the organization.
    """

    def has_permission(self, request, view):
        """Check if user is authenticated."""
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        """Check if user is a member of the organization."""
        # Determine the organization from the object
        if hasattr(obj, 'organization'):
            organization = obj.organization
        elif obj.__class__.__name__ == 'Organization':
            organization = obj
        else:
            return False

        # Check if user is an active member
        return organization.members.filter(
            user=request.user,
            is_active=True
        ).exists()


class IsOrganizationOwnerOrAdmin(permissions.BasePermission):
    """
    Permission to check if user is owner or admin of the organization.
    """

    def has_permission(self, request, view):
        """Check if user is authenticated."""
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        """Check if user is owner or admin."""
        # Determine the organization from the object
        if hasattr(obj, 'organization'):
            organization = obj.organization
        elif obj.__class__.__name__ == 'Organization':
            organization = obj
        else:
            return False

        # Check if user is owner
        if organization.owner == request.user:
            return True

        # Check if user is admin
        try:
            member = organization.members.get(
                user=request.user,
                is_active=True
            )
            return member.role.role_type in ['owner', 'admin']
        except:
            return False


class CanManageMembers(permissions.BasePermission):
    """
    Permission to check if user can manage organization members.
    """

    def has_permission(self, request, view):
        """Check if user is authenticated."""
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        """Check if user can manage members."""
        # Determine the organization from the object
        if hasattr(obj, 'organization'):
            organization = obj.organization
        else:
            return False

        # Check if user has members:create, members:update, or members:delete permission
        from .services import OrganizationService

        action_map = {
            'POST': 'create',
            'PUT': 'update',
            'PATCH': 'update',
            'DELETE': 'delete',
        }

        action = action_map.get(request.method, 'read')
        return OrganizationService.user_has_permission(
            request.user,
            organization,
            'members',
            action
        )


class CanManageRoles(permissions.BasePermission):
    """
    Permission to check if user can manage organization roles.
    """

    def has_permission(self, request, view):
        """Check if user is authenticated."""
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        """Check if user can manage roles."""
        # Determine the organization from the object
        if hasattr(obj, 'organization'):
            organization = obj.organization
        else:
            return False

        # Only owner and admin can manage roles
        try:
            member = organization.members.get(
                user=request.user,
                is_active=True
            )
            return member.role.role_type in ['owner', 'admin']
        except:
            return False


class HasModulePermission(permissions.BasePermission):
    """
    Generic permission to check if user has specific module permission.
    Must set `required_module` and `required_action` on the view.
    """

    def has_permission(self, request, view):
        """Check if user is authenticated."""
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        """Check if user has module permission."""
        # Determine the organization from the object
        if hasattr(obj, 'organization'):
            organization = obj.organization
        else:
            return False

        # Get required module and action from view
        required_module = getattr(view, 'required_module', None)
        required_action = getattr(view, 'required_action', None)

        if not required_module or not required_action:
            return False

        # Check permission
        from .services import OrganizationService
        return OrganizationService.user_has_permission(
            request.user,
            organization,
            required_module,
            required_action
        )


class IsOrganizationOwner(permissions.BasePermission):
    """
    Permission to check if user is the owner of the organization.
    """

    def has_permission(self, request, view):
        """Check if user is authenticated."""
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        """Check if user is owner."""
        # Determine the organization from the object
        if hasattr(obj, 'organization'):
            organization = obj.organization
        elif obj.__class__.__name__ == 'Organization':
            organization = obj
        else:
            return False

        return organization.owner == request.user
