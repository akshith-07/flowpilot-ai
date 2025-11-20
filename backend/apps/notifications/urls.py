"""URL configuration for Notifications app."""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .viewsets import NotificationViewSet, NotificationPreferenceViewSet, AlertRuleViewSet

app_name = 'notifications'

router = DefaultRouter()
router.register(r'', NotificationViewSet, basename='notification')
router.register(r'preferences', NotificationPreferenceViewSet, basename='notification-preference')
router.register(r'alert-rules', AlertRuleViewSet, basename='alert-rule')

urlpatterns = [
    path('', include(router.urls)),
]
