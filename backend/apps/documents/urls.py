"""URL configuration for Documents app."""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .viewsets import DocumentViewSet, DocumentPageViewSet, DocumentExtractionViewSet

app_name = 'documents'

router = DefaultRouter()
router.register(r'', DocumentViewSet, basename='document')
router.register(r'pages', DocumentPageViewSet, basename='document-page')
router.register(r'extractions', DocumentExtractionViewSet, basename='document-extraction')

urlpatterns = [
    path('', include(router.urls)),
]
