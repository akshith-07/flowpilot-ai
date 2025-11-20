"""
API viewsets for Notifications app.
"""
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from core.exceptions import ValidationError
from core.permissions import IsOrganizationMember
from .models import Notification, NotificationPreference, AlertRule
from .serializers import (
    NotificationSerializer, NotificationPreferenceSerializer,
    AlertRuleSerializer, NotificationMarkReadSerializer
)
from .services import NotificationService
import logging

logger = logging.getLogger(__name__)


class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for notifications (read-only).

    list: GET /api/v1/notifications/
    retrieve: GET /api/v1/notifications/{id}/
    """

    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['notification_type', 'channel', 'is_read']
    ordering = ['-created_at']

    def get_queryset(self):
        """Filter notifications by user."""
        return Notification.objects.filter(
            recipient=self.request.user
        ).select_related('recipient', 'organization')

    @action(detail=False, methods=['post'])
    def mark_read(self, request):
        """
        Mark notifications as read.

        POST /api/v1/notifications/mark-read/
        """
        serializer = NotificationMarkReadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        notification_ids = serializer.validated_data['notification_ids']

        # Update notifications
        updated = Notification.objects.filter(
            id__in=notification_ids,
            recipient=request.user,
            is_read=False
        ).update(is_read=True, read_at=timezone.now())

        return Response({
            'success': True,
            'message': f'{updated} notifications marked as read.'
        })

    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        """
        Mark all notifications as read for the current user.

        POST /api/v1/notifications/mark-all-read/
        """
        updated = Notification.objects.filter(
            recipient=request.user,
            is_read=False
        ).update(is_read=True, read_at=timezone.now())

        return Response({
            'success': True,
            'message': f'{updated} notifications marked as read.'
        })

    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        """
        Get count of unread notifications.

        GET /api/v1/notifications/unread-count/
        """
        count = Notification.objects.filter(
            recipient=request.user,
            is_read=False
        ).count()

        return Response({
            'success': True,
            'data': {
                'unread_count': count
            }
        })


class NotificationPreferenceViewSet(viewsets.ModelViewSet):
    """
    ViewSet for notification preferences.

    list: GET /api/v1/notifications/preferences/
    create: POST /api/v1/notifications/preferences/
    retrieve: GET /api/v1/notifications/preferences/{id}/
    update: PUT/PATCH /api/v1/notifications/preferences/{id}/
    destroy: DELETE /api/v1/notifications/preferences/{id}/
    """

    serializer_class = NotificationPreferenceSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['notification_type']

    def get_queryset(self):
        """Filter preferences by user."""
        return NotificationPreference.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """Set user on create."""
        serializer.save(user=self.request.user)


class AlertRuleViewSet(viewsets.ModelViewSet):
    """
    ViewSet for alert rules.

    list: GET /api/v1/notifications/alert-rules/
    create: POST /api/v1/notifications/alert-rules/
    retrieve: GET /api/v1/notifications/alert-rules/{id}/
    update: PUT/PATCH /api/v1/notifications/alert-rules/{id}/
    destroy: DELETE /api/v1/notifications/alert-rules/{id}/
    """

    serializer_class = AlertRuleSerializer
    permission_classes = [permissions.IsAuthenticated, IsOrganizationMember]
    filterset_fields = ['rule_type', 'is_active']
    ordering = ['-created_at']

    def get_queryset(self):
        """Filter alert rules by organization."""
        if not self.request.organization:
            return AlertRule.objects.none()

        return AlertRule.objects.filter(organization=self.request.organization)

    def perform_create(self, serializer):
        """Set organization on create."""
        serializer.save(organization=self.request.organization)
