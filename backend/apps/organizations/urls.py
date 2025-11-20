"""
URL configuration for Organizations app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .viewsets import (
    OrganizationViewSet, OrganizationMemberViewSet, RoleViewSet,
    DepartmentViewSet, InvitationViewSet, UsageQuotaViewSet
)

app_name = 'organizations'

router = DefaultRouter()
router.register(r'organizations', OrganizationViewSet, basename='organization')
router.register(r'members', OrganizationMemberViewSet, basename='member')
router.register(r'roles', RoleViewSet, basename='role')
router.register(r'departments', DepartmentViewSet, basename='department')
router.register(r'invitations', InvitationViewSet, basename='invitation')
router.register(r'quotas', UsageQuotaViewSet, basename='quota')

urlpatterns = [
    path('', include(router.urls)),
]
