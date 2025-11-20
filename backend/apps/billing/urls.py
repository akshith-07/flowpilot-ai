"""URL configuration for Billing app."""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .viewsets import (
    SubscriptionPlanViewSet, OrganizationSubscriptionViewSet,
    BillingUsageViewSet, InvoiceViewSet, APIKeyViewSet
)

app_name = 'billing'

router = DefaultRouter()
router.register(r'plans', SubscriptionPlanViewSet, basename='subscription-plan')
router.register(r'subscriptions', OrganizationSubscriptionViewSet, basename='organization-subscription')
router.register(r'usage', BillingUsageViewSet, basename='billing-usage')
router.register(r'invoices', InvoiceViewSet, basename='invoice')
router.register(r'api-keys', APIKeyViewSet, basename='api-key')

urlpatterns = [
    path('', include(router.urls)),
]
