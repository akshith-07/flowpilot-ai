"""
URL configuration for Users app - Authentication endpoints.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .viewsets import AuthViewSet, MFAViewSet

router = DefaultRouter()
router.register(r'', AuthViewSet, basename='auth')
router.register(r'mfa', MFAViewSet, basename='mfa')

urlpatterns = [
    path('', include(router.urls)),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
