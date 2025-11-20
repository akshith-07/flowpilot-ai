"""
URL configuration for Users app - User and Session endpoints.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .viewsets import UserViewSet, SessionViewSet

router = DefaultRouter()
router.register(r'', UserViewSet, basename='user')
router.register(r'sessions', SessionViewSet, basename='session')

urlpatterns = [
    path('', include(router.urls)),
]
