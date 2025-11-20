"""
URL configuration for Executions app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .viewsets import (
    WorkflowExecutionViewSet, ExecutionStepViewSet,
    ExecutionLogViewSet, AIRequestViewSet
)

app_name = 'executions'

router = DefaultRouter()
router.register(r'executions', WorkflowExecutionViewSet, basename='execution')
router.register(r'steps', ExecutionStepViewSet, basename='step')
router.register(r'logs', ExecutionLogViewSet, basename='log')
router.register(r'ai-requests', AIRequestViewSet, basename='ai-request')

urlpatterns = [
    path('', include(router.urls)),
]
