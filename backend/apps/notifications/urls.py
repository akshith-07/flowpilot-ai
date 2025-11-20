"""URL configuration for Notifications app."""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

app_name = 'notifications'

router = DefaultRouter()

urlpatterns = [
    path('', include(router.urls)),
]
