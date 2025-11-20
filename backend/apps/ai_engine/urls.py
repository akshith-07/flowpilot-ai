"""URL configuration for AI Engine app."""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .viewsets import PromptTemplateViewSet, AIEngineViewSet

app_name = 'ai_engine'

router = DefaultRouter()
router.register(r'templates', PromptTemplateViewSet, basename='prompt-template')
router.register(r'', AIEngineViewSet, basename='ai-engine')

urlpatterns = [
    path('', include(router.urls)),
]
