"""
API viewsets for Connectors app.
"""
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from core.exceptions import ValidationError
from core.permissions import IsOrganizationMember
from .models import Connector, ConnectorCredential, ConnectorWebhook, ConnectorSyncLog
from .serializers import (
    ConnectorSerializer, ConnectorCreateSerializer, ConnectorCredentialSerializer,
    ConnectorWebhookSerializer, ConnectorSyncLogSerializer,
    ConnectorOAuthInitiateSerializer, ConnectorOAuthCallbackSerializer,
    ConnectorTestSerializer
)
from .services import ConnectorService
import logging

logger = logging.getLogger(__name__)


class ConnectorViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing connectors.

    list: GET /api/v1/connectors/
    create: POST /api/v1/connectors/
    retrieve: GET /api/v1/connectors/{id}/
    update: PUT/PATCH /api/v1/connectors/{id}/
    destroy: DELETE /api/v1/connectors/{id}/
    """

    serializer_class = ConnectorSerializer
    permission_classes = [permissions.IsAuthenticated, IsOrganizationMember]
    filterset_fields = ['provider', 'is_active', 'is_connected']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at', 'last_sync_at']
    ordering = ['-created_at']

    def get_queryset(self):
        """Filter connectors by organization."""
        if not self.request.organization:
            return Connector.objects.none()

        return Connector.objects.filter(
            organization=self.request.organization
        ).select_related('organization')

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'create':
            return ConnectorCreateSerializer
        return ConnectorSerializer

    @action(detail=True, methods=['post'])
    def test_connection(self, request, pk=None):
        """
        Test connector connection.

        POST /api/v1/connectors/{id}/test-connection/
        """
        connector = self.get_object()
        serializer = ConnectorTestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            result = ConnectorService.test_connection(
                connector,
                test_type=serializer.validated_data.get('test_type', 'connection'),
                test_parameters=serializer.validated_data.get('test_parameters', {})
            )

            return Response({
                'success': True,
                'data': result
            })

        except Exception as e:
            logger.error(f'Connector test failed for {connector.id}: {str(e)}')
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def sync(self, request, pk=None):
        """
        Trigger manual sync for connector.

        POST /api/v1/connectors/{id}/sync/
        """
        connector = self.get_object()

        if not connector.is_connected:
            raise ValidationError('Connector is not connected. Please authorize first.')

        try:
            # Trigger async sync task
            from .tasks import sync_connector
            task = sync_connector.delay(str(connector.id))

            return Response({
                'success': True,
                'message': 'Sync initiated.',
                'data': {
                    'task_id': task.id
                }
            })

        except Exception as e:
            logger.error(f'Failed to initiate sync for connector {connector.id}: {str(e)}')
            raise ValidationError(f'Failed to initiate sync: {str(e)}')

    @action(detail=False, methods=['get'])
    def providers(self, request):
        """
        List all available connector providers.

        GET /api/v1/connectors/providers/
        """
        providers = [
            {
                'id': choice[0],
                'name': choice[1],
                'category': ConnectorService.get_provider_category(choice[0]),
                'supports_oauth': ConnectorService.supports_oauth(choice[0]),
                'required_scopes': ConnectorService.get_required_scopes(choice[0])
            }
            for choice in Connector.PROVIDER_CHOICES
        ]

        return Response({
            'success': True,
            'data': providers
        })

    @action(detail=True, methods=['get'])
    def sync_history(self, request, pk=None):
        """
        Get sync history for connector.

        GET /api/v1/connectors/{id}/sync-history/
        """
        connector = self.get_object()

        sync_logs = ConnectorSyncLog.objects.filter(connector=connector).order_by('-created_at')

        # Apply pagination
        page = self.paginate_queryset(sync_logs)
        if page is not None:
            serializer = ConnectorSyncLogSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = ConnectorSyncLogSerializer(sync_logs, many=True)
        return Response({
            'success': True,
            'data': serializer.data
        })


class ConnectorOAuthViewSet(viewsets.GenericViewSet):
    """
    ViewSet for OAuth authentication flow.
    """

    permission_classes = [permissions.IsAuthenticated, IsOrganizationMember]

    @action(detail=False, methods=['post'])
    def initiate(self, request):
        """
        Initiate OAuth authorization flow.

        POST /api/v1/connectors/oauth/initiate/

        Returns authorization URL for user to visit.
        """
        serializer = ConnectorOAuthInitiateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            result = ConnectorService.initiate_oauth(
                organization=request.organization,
                user=request.user,
                provider=serializer.validated_data['provider'],
                redirect_uri=serializer.validated_data.get('redirect_uri'),
                scopes=serializer.validated_data.get('scopes')
            )

            return Response({
                'success': True,
                'data': result
            })

        except Exception as e:
            logger.error(f'OAuth initiation failed: {str(e)}')
            raise ValidationError(f'Failed to initiate OAuth: {str(e)}')

    @action(detail=False, methods=['post'])
    def callback(self, request):
        """
        Handle OAuth callback.

        POST /api/v1/connectors/oauth/callback/

        Exchanges authorization code for access token.
        """
        serializer = ConnectorOAuthCallbackSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            result = ConnectorService.handle_oauth_callback(
                code=serializer.validated_data['code'],
                state=serializer.validated_data['state'],
                user=request.user
            )

            return Response({
                'success': True,
                'message': 'Connector authorized successfully.',
                'data': {
                    'connector': ConnectorSerializer(result['connector']).data
                }
            })

        except Exception as e:
            logger.error(f'OAuth callback failed: {str(e)}')
            raise ValidationError(f'OAuth authorization failed: {str(e)}')

    @action(detail=True, methods=['post'], url_path='revoke/(?P<connector_id>[^/.]+)')
    def revoke(self, request, connector_id=None):
        """
        Revoke OAuth access for a connector.

        POST /api/v1/connectors/oauth/revoke/{connector_id}/
        """
        connector = get_object_or_404(
            Connector,
            id=connector_id,
            organization=request.organization
        )

        try:
            ConnectorService.revoke_oauth(connector)

            return Response({
                'success': True,
                'message': 'Connector access revoked successfully.'
            })

        except Exception as e:
            logger.error(f'Failed to revoke OAuth for connector {connector_id}: {str(e)}')
            raise ValidationError(f'Failed to revoke access: {str(e)}')


class ConnectorWebhookViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for managing connector webhooks.

    list: GET /api/v1/connectors/webhooks/
    retrieve: GET /api/v1/connectors/webhooks/{id}/
    """

    serializer_class = ConnectorWebhookSerializer
    permission_classes = [permissions.IsAuthenticated, IsOrganizationMember]
    filterset_fields = ['connector', 'event_type', 'is_active']
    ordering = ['-created_at']

    def get_queryset(self):
        """Filter webhooks by organization."""
        if not self.request.organization:
            return ConnectorWebhook.objects.none()

        return ConnectorWebhook.objects.filter(
            connector__organization=request.organization
        ).select_related('connector')

    @action(detail=True, methods=['post'])
    def verify(self, request, pk=None):
        """
        Verify webhook configuration.

        POST /api/v1/connectors/webhooks/{id}/verify/
        """
        webhook = self.get_object()

        try:
            success = ConnectorService.verify_webhook(webhook)

            if success:
                return Response({
                    'success': True,
                    'message': 'Webhook verified successfully.'
                })
            else:
                return Response({
                    'success': False,
                    'message': 'Webhook verification failed.'
                }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logger.error(f'Webhook verification failed for {webhook.id}: {str(e)}')
            raise ValidationError(f'Webhook verification failed: {str(e)}')
