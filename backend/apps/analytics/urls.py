"""URL configuration for Analytics app."""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

app_name = 'analytics'

router = DefaultRouter()

urlpatterns = [
    path('', include(router.urls)),
]
