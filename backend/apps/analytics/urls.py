"""URL configuration for Analytics app."""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .viewsets import AnalyticsViewSet, DailyMetricsViewSet, UserActivityViewSet, ErrorLogViewSet

app_name = 'analytics'

router = DefaultRouter()
router.register(r'', AnalyticsViewSet, basename='analytics')
router.register(r'daily-metrics', DailyMetricsViewSet, basename='daily-metrics')
router.register(r'user-activity', UserActivityViewSet, basename='user-activity')
router.register(r'error-logs', ErrorLogViewSet, basename='error-log')

urlpatterns = [
    path('', include(router.urls)),
]
