"""URL configuration for AI Engine app."""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

app_name = 'ai_engine'

router = DefaultRouter()
# Add viewsets here when ready

urlpatterns = [
    path('', include(router.urls)),
]
