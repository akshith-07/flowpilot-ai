"""
Quota Enforcement Middleware for billing limits.
Enforces usage quotas based on organization subscription plans.
"""
from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse
from apps.billing.models import OrganizationSubscription, BillingUsage
from apps.organizations.models import UsageQuota
from django.utils import timezone


class QuotaEnforcementMiddleware(MiddlewareMixin):
    """
    Middleware to enforce usage quotas for organizations.

    Checks quotas for:
    - Workflow executions
    - AI API calls
    - Document uploads
    - API requests

    Returns 429 Too Many Requests if quota exceeded.
    """

    # Endpoints that consume quotas
    QUOTA_ENDPOINTS = {
        'workflow_execution': ['/api/v1/workflows/', '/api/v1/executions/'],
        'ai_request': ['/api/v1/ai-engine/', '/api/v1/executions/'],
        'document_upload': ['/api/v1/documents/'],
        'api_request': ['/api/v1/'],
    }

    def process_request(self, request):
        """Check quota before processing request."""
        # Skip for non-API requests or unauthenticated users
        if not request.path.startswith('/api/v1/'):
            return None

        if not request.user or not request.user.is_authenticated:
            return None

        # Skip for safe methods (GET, HEAD, OPTIONS)
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return None

        # Skip if no organization context
        if not hasattr(request, 'organization') or not request.organization:
            return None

        organization = request.organization

        # Check quota based on endpoint
        quota_type = self._get_quota_type(request.path)
        if not quota_type:
            return None

        # Get organization's quota
        try:
            quota = UsageQuota.objects.get(
                organization=organization,
                is_active=True
            )

            # Check if quota exceeded
            if self._is_quota_exceeded(organization, quota, quota_type):
                return JsonResponse({
                    'error': 'Quota exceeded',
                    'detail': f'Your organization has exceeded the {quota_type} quota for this billing period.',
                    'quota_type': quota_type,
                    'current_usage': getattr(quota, f'used_{quota_type}', 0),
                    'limit': getattr(quota, f'max_{quota_type}', 0),
                }, status=429)

        except UsageQuota.DoesNotExist:
            # No quota set, allow by default (or you can deny)
            pass
        except Exception as e:
            # Log error but don't block request
            print(f"Quota check error: {e}")
            pass

        return None

    def process_response(self, request, response):
        """Track usage after successful request."""
        # Only track successful requests (2xx status codes)
        if not 200 <= response.status_code < 300:
            return response

        # Skip for non-API requests
        if not request.path.startswith('/api/v1/'):
            return response

        # Skip if no organization context
        if not hasattr(request, 'organization') or not request.organization:
            return response

        # Track usage based on endpoint
        quota_type = self._get_quota_type(request.path)
        if quota_type and request.method in ['POST', 'PUT', 'PATCH']:
            try:
                self._increment_usage(request.organization, quota_type)
            except Exception as e:
                # Log error but don't fail response
                print(f"Usage tracking error: {e}")

        # Add quota headers to response
        self._add_quota_headers(request, response)

        return response

    def _get_quota_type(self, path):
        """Determine quota type based on request path."""
        if any(endpoint in path for endpoint in self.QUOTA_ENDPOINTS['workflow_execution']):
            return 'workflow_executions'
        elif any(endpoint in path for endpoint in self.QUOTA_ENDPOINTS['ai_request']):
            return 'ai_requests'
        elif any(endpoint in path for endpoint in self.QUOTA_ENDPOINTS['document_upload']):
            return 'document_uploads'
        elif path.startswith('/api/v1/'):
            return 'api_requests'
        return None

    def _is_quota_exceeded(self, organization, quota, quota_type):
        """Check if quota is exceeded for the given type."""
        used_field = f'used_{quota_type}'
        max_field = f'max_{quota_type}'

        used = getattr(quota, used_field, 0)
        max_allowed = getattr(quota, max_field, float('inf'))

        return used >= max_allowed

    def _increment_usage(self, organization, quota_type):
        """Increment usage counter for the given quota type."""
        try:
            quota = UsageQuota.objects.get(
                organization=organization,
                is_active=True
            )

            # Increment the appropriate field
            used_field = f'used_{quota_type}'
            current_value = getattr(quota, used_field, 0)
            setattr(quota, used_field, current_value + 1)
            quota.save(update_fields=[used_field, 'updated_at'])

            # Also track in BillingUsage for detailed analytics
            period_start = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            BillingUsage.objects.update_or_create(
                organization=organization,
                period_start=period_start,
                defaults={
                    'period_end': self._get_period_end(period_start),
                }
            )

        except UsageQuota.DoesNotExist:
            pass

    def _get_period_end(self, period_start):
        """Calculate period end date (end of month)."""
        import calendar
        from datetime import datetime

        year = period_start.year
        month = period_start.month
        last_day = calendar.monthrange(year, month)[1]

        return period_start.replace(
            day=last_day,
            hour=23,
            minute=59,
            second=59,
            microsecond=999999
        )

    def _add_quota_headers(self, request, response):
        """Add quota information to response headers."""
        if not hasattr(request, 'organization') or not request.organization:
            return

        try:
            quota = UsageQuota.objects.get(
                organization=request.organization,
                is_active=True
            )

            # Add headers for each quota type
            response['X-Quota-Workflows-Used'] = quota.used_workflow_executions
            response['X-Quota-Workflows-Limit'] = quota.max_workflow_executions
            response['X-Quota-AI-Used'] = quota.used_ai_requests
            response['X-Quota-AI-Limit'] = quota.max_ai_requests
            response['X-Quota-Documents-Used'] = quota.used_document_uploads
            response['X-Quota-Documents-Limit'] = quota.max_document_uploads
            response['X-Quota-API-Used'] = quota.used_api_requests
            response['X-Quota-API-Limit'] = quota.max_api_requests

        except UsageQuota.DoesNotExist:
            pass
