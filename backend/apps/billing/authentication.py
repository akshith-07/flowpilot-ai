"""
API Key Authentication for FlowPilot AI.
Allows authentication using API keys for programmatic access.
"""
from rest_framework import authentication, exceptions
from django.contrib.auth import get_user_model
from apps.billing.models import APIKey
from django.utils import timezone
from apps.analytics.models import UserActivity

User = get_user_model()


class APIKeyAuthentication(authentication.BaseAuthentication):
    """
    Custom authentication class for API key authentication.

    Expects API key in:
    1. Authorization header: "Authorization: ApiKey <key>"
    2. X-API-Key header: "X-API-Key: <key>"
    3. api_key query parameter: "?api_key=<key>"

    API keys are associated with an organization and user.
    """

    keyword = 'ApiKey'

    def authenticate(self, request):
        """
        Authenticate the request using an API key.

        Returns:
            tuple: (user, api_key) if authentication successful
            None: if authentication not attempted

        Raises:
            AuthenticationFailed: if authentication fails
        """
        api_key_value = self.get_api_key(request)

        if not api_key_value:
            return None

        # Validate and get API key
        try:
            api_key = APIKey.objects.select_related(
                'organization', 'created_by'
            ).get(
                key=api_key_value,
                is_active=True
            )
        except APIKey.DoesNotExist:
            raise exceptions.AuthenticationFailed('Invalid API key')

        # Check if API key is expired
        if api_key.expires_at and api_key.expires_at < timezone.now():
            raise exceptions.AuthenticationFailed('API key has expired')

        # Update last used timestamp
        api_key.last_used_at = timezone.now()
        api_key.save(update_fields=['last_used_at'])

        # Track usage in analytics
        try:
            UserActivity.objects.create(
                user=api_key.created_by,
                organization=api_key.organization,
                action='api_key_used',
                resource_type='api_key',
                resource_id=str(api_key.id),
                metadata={
                    'api_key_name': api_key.name,
                    'path': request.path,
                    'method': request.method,
                }
            )
        except Exception:
            # Don't fail authentication if activity tracking fails
            pass

        # Set organization context for middleware
        request.organization = api_key.organization

        # Return the user who created the API key
        return (api_key.created_by, api_key)

    def get_api_key(self, request):
        """
        Extract API key from request.

        Checks in order:
        1. Authorization header
        2. X-API-Key header
        3. api_key query parameter
        """
        # 1. Check Authorization header
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if auth_header.startswith(f'{self.keyword} '):
            return auth_header.split(' ')[1]

        # 2. Check X-API-Key header
        api_key_header = request.META.get('HTTP_X_API_KEY', '')
        if api_key_header:
            return api_key_header

        # 3. Check query parameter (least preferred, but useful for webhooks)
        api_key_param = request.GET.get('api_key', '')
        if api_key_param:
            return api_key_param

        return None

    def authenticate_header(self, request):
        """
        Return authentication header for 401 responses.
        """
        return self.keyword
