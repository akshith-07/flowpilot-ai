"""
API viewsets for Analytics app.
"""
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from datetime import timedelta
from core.exceptions import ValidationError
from core.permissions import IsOrganizationMember
from .models import DailyMetrics, UserActivity, ErrorLog
from .serializers import (
    DailyMetricsSerializer, UserActivitySerializer,
    ErrorLogSerializer, DashboardMetricsSerializer
)
from .services import AnalyticsService
import logging

logger = logging.getLogger(__name__)


class AnalyticsViewSet(viewsets.GenericViewSet):
    """
    ViewSet for analytics and reporting.
    """

    permission_classes = [permissions.IsAuthenticated, IsOrganizationMember]

    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        """
        Get dashboard metrics.

        GET /api/v1/analytics/dashboard/?period=week
        """
        period = request.query_params.get('period', 'week')

        try:
            metrics = AnalyticsService.get_dashboard_metrics(
                organization=request.organization,
                period=period
            )

            return Response({
                'success': True,
                'data': metrics
            })

        except Exception as e:
            logger.error(f'Failed to get dashboard metrics: {str(e)}')
            raise ValidationError(f'Failed to get metrics: {str(e)}')

    @action(detail=False, methods=['get'])
    def workflows(self, request):
        """
        Get workflow analytics.

        GET /api/v1/analytics/workflows/
        """
        try:
            analytics = AnalyticsService.get_workflow_analytics(
                organization=request.organization
            )

            return Response({
                'success': True,
                'data': analytics
            })

        except Exception as e:
            logger.error(f'Failed to get workflow analytics: {str(e)}')
            raise ValidationError(f'Failed to get workflow analytics: {str(e)}')

    @action(detail=False, methods=['get'])
    def ai_usage(self, request):
        """
        Get AI usage analytics.

        GET /api/v1/analytics/ai-usage/
        """
        try:
            usage = AnalyticsService.get_ai_usage_analytics(
                organization=request.organization
            )

            return Response({
                'success': True,
                'data': usage
            })

        except Exception as e:
            logger.error(f'Failed to get AI usage analytics: {str(e)}')
            raise ValidationError(f'Failed to get AI usage analytics: {str(e)}')

    @action(detail=False, methods=['get'])
    def errors(self, request):
        """
        Get error analytics.

        GET /api/v1/analytics/errors/
        """
        try:
            errors = AnalyticsService.get_error_analytics(
                organization=request.organization
            )

            return Response({
                'success': True,
                'data': errors
            })

        except Exception as e:
            logger.error(f'Failed to get error analytics: {str(e)}')
            raise ValidationError(f'Failed to get error analytics: {str(e)}')


class DailyMetricsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for daily metrics (read-only).

    list: GET /api/v1/analytics/daily-metrics/
    retrieve: GET /api/v1/analytics/daily-metrics/{id}/
    """

    serializer_class = DailyMetricsSerializer
    permission_classes = [permissions.IsAuthenticated, IsOrganizationMember]
    filterset_fields = ['date']
    ordering = ['-date']

    def get_queryset(self):
        """Filter metrics by organization."""
        if not self.request.organization:
            return DailyMetrics.objects.none()

        return DailyMetrics.objects.filter(organization=self.request.organization)


class UserActivityViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for user activity (read-only).

    list: GET /api/v1/analytics/user-activity/
    retrieve: GET /api/v1/analytics/user-activity/{id}/
    """

    serializer_class = UserActivitySerializer
    permission_classes = [permissions.IsAuthenticated, IsOrganizationMember]
    filterset_fields = ['user', 'action', 'resource_type']
    ordering = ['-created_at']

    def get_queryset(self):
        """Filter activity by organization."""
        if not self.request.organization:
            return UserActivity.objects.none()

        return UserActivity.objects.filter(
            organization=self.request.organization
        ).select_related('user', 'organization')


class ErrorLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for error logs (read-only).

    list: GET /api/v1/analytics/error-logs/
    retrieve: GET /api/v1/analytics/error-logs/{id}/
    """

    serializer_class = ErrorLogSerializer
    permission_classes = [permissions.IsAuthenticated, IsOrganizationMember]
    filterset_fields = ['error_type', 'severity', 'resolved']
    ordering = ['-created_at']

    def get_queryset(self):
        """Filter error logs by organization."""
        if not self.request.organization:
            return ErrorLog.objects.none()

        return ErrorLog.objects.filter(organization=self.request.organization)

    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        """
        Mark error as resolved.

        POST /api/v1/analytics/error-logs/{id}/resolve/
        """
        error_log = self.get_object()

        error_log.resolved = True
        error_log.resolved_at = timezone.now()
        error_log.save(update_fields=['resolved', 'resolved_at'])

        return Response({
            'success': True,
            'message': 'Error marked as resolved.'
        })
