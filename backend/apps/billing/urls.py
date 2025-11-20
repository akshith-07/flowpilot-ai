"""URL configuration for Billing app."""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

app_name = 'billing'

router = DefaultRouter()

urlpatterns = [
    path('', include(router.urls)),
]
