"""
SSO URL configuration.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    SSOProviderViewSet, SSOConnectionViewSet,
    SSOSessionViewSet, SSOAuditLogViewSet,
    SSOLoginView, SSOCallbackView,
    SAMLACSView, SAMLMetadataView
)

app_name = 'sso'

router = DefaultRouter()
router.register(r'providers', SSOProviderViewSet, basename='sso-provider')
router.register(r'connections', SSOConnectionViewSet, basename='sso-connection')
router.register(r'sessions', SSOSessionViewSet, basename='sso-session')
router.register(r'audit-logs', SSOAuditLogViewSet, basename='sso-audit-log')

urlpatterns = [
    # Router URLs
    path('', include(router.urls)),

    # SSO authentication flows
    path('login/', SSOLoginView.as_view(), name='sso-login'),
    path('callback/', SSOCallbackView.as_view(), name='sso-callback'),

    # SAML specific endpoints
    path('saml/acs/', SAMLACSView.as_view(), name='saml-acs'),
    path('saml/metadata/<uuid:connection_id>/', SAMLMetadataView.as_view(), name='saml-metadata'),
]
