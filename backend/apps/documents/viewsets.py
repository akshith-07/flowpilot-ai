"""
API viewsets for Documents app.
"""
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.core.files.storage import default_storage
from core.exceptions import ValidationError
from core.permissions import IsOrganizationMember
from .models import Document, DocumentPage, DocumentExtraction
from .serializers import (
    DocumentSerializer, DocumentUploadSerializer, DocumentPageSerializer,
    DocumentExtractionSerializer, DocumentExtractionRequestSerializer,
    DocumentSearchSerializer
)
from .services import DocumentService
import logging

logger = logging.getLogger(__name__)


class DocumentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing documents.

    list: GET /api/v1/documents/
    create: POST /api/v1/documents/  (multipart/form-data for file upload)
    retrieve: GET /api/v1/documents/{id}/
    update: PATCH /api/v1/documents/{id}/
    destroy: DELETE /api/v1/documents/{id}/
    """

    serializer_class = DocumentSerializer
    permission_classes = [permissions.IsAuthenticated, IsOrganizationMember]
    parser_classes = [MultiPartParser, FormParser]
    filterset_fields = ['file_type', 'status']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at', 'file_size']
    ordering = ['-created_at']

    def get_queryset(self):
        """Filter documents by organization."""
        if not self.request.organization:
            return Document.objects.none()

        return Document.objects.filter(
            organization=self.request.organization
        ).select_related('uploaded_by', 'organization').prefetch_related('pages', 'extractions')

    def create(self, request, *args, **kwargs):
        """Handle document upload."""
        serializer = DocumentUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            # Upload and process document
            document = DocumentService.upload_document(
                organization=request.organization,
                uploaded_by=request.user,
                file=serializer.validated_data['file'],
                name=serializer.validated_data.get('name'),
                description=serializer.validated_data.get('description', ''),
                file_type=serializer.validated_data.get('file_type'),
                extract_text=serializer.validated_data.get('extract_text', True),
                generate_embeddings=serializer.validated_data.get('generate_embeddings', False)
            )

            return Response({
                'success': True,
                'message': 'Document uploaded successfully.',
                'data': DocumentSerializer(document).data
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            logger.error(f'Document upload failed: {str(e)}')
            raise ValidationError(f'Document upload failed: {str(e)}')

    @action(detail=True, methods=['post'])
    def extract(self, request, pk=None):
        """
        Extract data from document.

        POST /api/v1/documents/{id}/extract/
        """
        document = self.get_object()
        serializer = DocumentExtractionRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            # Trigger extraction task
            from .tasks import extract_document_data
            task = extract_document_data.delay(
                str(document.id),
                serializer.validated_data['extraction_type'],
                serializer.validated_data.get('extraction_config', {})
            )

            return Response({
                'success': True,
                'message': 'Extraction initiated.',
                'data': {
                    'task_id': task.id
                }
            })

        except Exception as e:
            logger.error(f'Document extraction failed: {str(e)}')
            raise ValidationError(f'Document extraction failed: {str(e)}')

    @action(detail=False, methods=['post'])
    def search(self, request):
        """
        Search documents.

        POST /api/v1/documents/search/
        """
        serializer = DocumentSearchSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            results = DocumentService.search_documents(
                organization=request.organization,
                query=serializer.validated_data['query'],
                search_type=serializer.validated_data.get('search_type', 'text'),
                file_type=serializer.validated_data.get('file_type'),
                limit=serializer.validated_data.get('limit', 10)
            )

            return Response({
                'success': True,
                'data': results
            })

        except Exception as e:
            logger.error(f'Document search failed: {str(e)}')
            raise ValidationError(f'Document search failed: {str(e)}')

    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        """
        Download document file.

        GET /api/v1/documents/{id}/download/
        """
        document = self.get_object()

        try:
            file_url = DocumentService.get_download_url(document)

            return Response({
                'success': True,
                'data': {
                    'download_url': file_url
                }
            })

        except Exception as e:
            logger.error(f'Document download failed: {str(e)}')
            raise ValidationError(f'Document download failed: {str(e)}')


class DocumentPageViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for document pages (read-only).

    list: GET /api/v1/documents/pages/
    retrieve: GET /api/v1/documents/pages/{id}/
    """

    serializer_class = DocumentPageSerializer
    permission_classes = [permissions.IsAuthenticated, IsOrganizationMember]
    filterset_fields = ['document']
    ordering = ['page_number']

    def get_queryset(self):
        """Filter pages by organization."""
        if not self.request.organization:
            return DocumentPage.objects.none()

        return DocumentPage.objects.filter(
            document__organization=self.request.organization
        ).select_related('document')


class DocumentExtractionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for document extractions (read-only).

    list: GET /api/v1/documents/extractions/
    retrieve: GET /api/v1/documents/extractions/{id}/
    """

    serializer_class = DocumentExtractionSerializer
    permission_classes = [permissions.IsAuthenticated, IsOrganizationMember]
    filterset_fields = ['document', 'extraction_type']
    ordering = ['-created_at']

    def get_queryset(self):
        """Filter extractions by organization."""
        if not self.request.organization:
            return DocumentExtraction.objects.none()

        return DocumentExtraction.objects.filter(
            document__organization=self.request.organization
        ).select_related('document', 'extracted_by')
