"""
Organization Context Middleware for multi-tenancy.
Injects organization context into requests based on user membership.
"""
from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse
from apps.organizations.models import Organization, OrganizationMember


class OrganizationContextMiddleware(MiddlewareMixin):
    """
    Middleware to inject organization context into the request.

    Extracts organization from:
    1. X-Organization-ID header
    2. organization_id query parameter
    3. User's default organization (first active membership)

    Sets request.organization for use in views and permissions.
    """

    def process_request(self, request):
        """Process incoming request to extract organization context."""
        request.organization = None

        # Skip for unauthenticated requests
        if not request.user or not request.user.is_authenticated:
            return None

        organization_id = None

        # 1. Try to get from header (preferred for API clients)
        organization_id = request.headers.get('X-Organization-ID')

        # 2. Try to get from query parameter (for web clients)
        if not organization_id:
            organization_id = request.GET.get('organization_id')

        # 3. Get user's default organization (first active membership)
        if not organization_id:
            try:
                membership = OrganizationMember.objects.filter(
                    user=request.user,
                    is_active=True
                ).select_related('organization').first()

                if membership:
                    organization_id = str(membership.organization.id)
            except Exception:
                pass

        # Validate and set organization
        if organization_id:
            try:
                # Verify user has access to this organization
                organization = Organization.objects.get(
                    id=organization_id,
                    is_active=True,
                    members__user=request.user,
                    members__is_active=True
                )
                request.organization = organization
            except Organization.DoesNotExist:
                # Invalid organization ID or user doesn't have access
                # Set to None, views can handle this appropriately
                pass

        return None

    def process_response(self, request, response):
        """Add organization ID to response headers if set."""
        if hasattr(request, 'organization') and request.organization:
            response['X-Organization-ID'] = str(request.organization.id)
        return response
