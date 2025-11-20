"""
URL configuration for Workflows app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .viewsets import (
    WorkflowViewSet, WorkflowTemplateViewSet, WorkflowVariableViewSet,
    WorkflowTriggerViewSet
)

app_name = 'workflows'

router = DefaultRouter()
router.register(r'workflows', WorkflowViewSet, basename='workflow')
router.register(r'templates', WorkflowTemplateViewSet, basename='template')
router.register(r'variables', WorkflowVariableViewSet, basename='variable')
router.register(r'triggers', WorkflowTriggerViewSet, basename='trigger')

urlpatterns = [
    path('', include(router.urls)),
]
