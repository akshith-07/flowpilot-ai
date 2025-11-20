"""URL configuration for Connectors app."""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

app_name = 'connectors'

router = DefaultRouter()
# Add viewsets here when ready

urlpatterns = [
    path('', include(router.urls)),
]
