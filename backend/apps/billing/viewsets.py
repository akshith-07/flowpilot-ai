"""
API viewsets for Billing app.
"""
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from core.exceptions import ValidationError
from core.permissions import IsOrganizationMember
from .models import SubscriptionPlan, OrganizationSubscription, BillingUsage, Invoice, APIKey
from .serializers import (
    SubscriptionPlanSerializer, OrganizationSubscriptionSerializer,
    BillingUsageSerializer, InvoiceSerializer, APIKeySerializer,
    APIKeyCreateSerializer
)
import logging

logger = logging.getLogger(__name__)


class SubscriptionPlanViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for subscription plans (read-only for customers).

    list: GET /api/v1/billing/plans/
    retrieve: GET /api/v1/billing/plans/{id}/
    """

    serializer_class = SubscriptionPlanSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = SubscriptionPlan.objects.filter(is_active=True).order_by('monthly_price')


class OrganizationSubscriptionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for organization subscriptions.

    list: GET /api/v1/billing/subscriptions/
    retrieve: GET /api/v1/billing/subscriptions/{id}/
    """

    serializer_class = OrganizationSubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated, IsOrganizationMember]

    def get_queryset(self):
        """Filter subscriptions by organization."""
        if not self.request.organization:
            return OrganizationSubscription.objects.none()

        return OrganizationSubscription.objects.filter(
            organization=self.request.organization
        ).select_related('plan', 'organization')

    @action(detail=True, methods=['post'])
    def upgrade(self, request, pk=None):
        """
        Upgrade subscription to a new plan.

        POST /api/v1/billing/subscriptions/{id}/upgrade/
        """
        subscription = self.get_object()
        new_plan_id = request.data.get('plan_id')

        if not new_plan_id:
            raise ValidationError('plan_id is required.')

        try:
            new_plan = SubscriptionPlan.objects.get(id=new_plan_id, is_active=True)

            # TODO: Integrate with Stripe for payment processing
            subscription.plan = new_plan
            subscription.save(update_fields=['plan'])

            return Response({
                'success': True,
                'message': 'Subscription upgraded successfully.',
                'data': OrganizationSubscriptionSerializer(subscription).data
            })

        except SubscriptionPlan.DoesNotExist:
            raise ValidationError('Invalid plan ID.')


class BillingUsageViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for billing usage (read-only).

    list: GET /api/v1/billing/usage/
    retrieve: GET /api/v1/billing/usage/{id}/
    """

    serializer_class = BillingUsageSerializer
    permission_classes = [permissions.IsAuthenticated, IsOrganizationMember]
    filterset_fields = ['usage_type', 'billing_period_start']
    ordering = ['-created_at']

    def get_queryset(self):
        """Filter usage by organization."""
        if not self.request.organization:
            return BillingUsage.objects.none()

        return BillingUsage.objects.filter(organization=self.request.organization)


class InvoiceViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for invoices (read-only).

    list: GET /api/v1/billing/invoices/
    retrieve: GET /api/v1/billing/invoices/{id}/
    """

    serializer_class = InvoiceSerializer
    permission_classes = [permissions.IsAuthenticated, IsOrganizationMember]
    filterset_fields = ['status']
    ordering = ['-created_at']

    def get_queryset(self):
        """Filter invoices by organization."""
        if not self.request.organization:
            return Invoice.objects.none()

        return Invoice.objects.filter(organization=self.request.organization)

    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        """
        Download invoice PDF.

        GET /api/v1/billing/invoices/{id}/download/
        """
        invoice = self.get_object()

        # TODO: Generate PDF or get from Stripe
        return Response({
            'success': True,
            'data': {
                'download_url': f'/invoices/{invoice.invoice_number}.pdf'
            }
        })


class APIKeyViewSet(viewsets.ModelViewSet):
    """
    ViewSet for API keys.

    list: GET /api/v1/billing/api-keys/
    create: POST /api/v1/billing/api-keys/
    retrieve: GET /api/v1/billing/api-keys/{id}/
    update: PATCH /api/v1/billing/api-keys/{id}/
    destroy: DELETE /api/v1/billing/api-keys/{id}/
    """

    permission_classes = [permissions.IsAuthenticated, IsOrganizationMember]
    filterset_fields = ['is_active']
    ordering = ['-created_at']

    def get_queryset(self):
        """Filter API keys by organization."""
        if not self.request.organization:
            return APIKey.objects.none()

        return APIKey.objects.filter(
            organization=self.request.organization
        ).select_related('organization', 'created_by')

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'create':
            return APIKeyCreateSerializer
        return APIKeySerializer

    @action(detail=True, methods=['post'])
    def rotate(self, request, pk=None):
        """
        Rotate API key (generate new key).

        POST /api/v1/billing/api-keys/{id}/rotate/
        """
        api_key = self.get_object()

        old_key, new_key = api_key.rotate_key()

        return Response({
            'success': True,
            'message': 'API key rotated successfully.',
            'data': {
                'id': str(api_key.id),
                'old_prefix': old_key[:8],
                'new_key': new_key,  # Show full key only once
                'new_prefix': api_key.prefix
            }
        })
