"""URL configuration for Documents app."""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

app_name = 'documents'

router = DefaultRouter()
# Add viewsets here when ready

urlpatterns = [
    path('', include(router.urls)),
]
