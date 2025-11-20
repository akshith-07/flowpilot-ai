"""
Business logic services for Documents app.
"""
import os
import uuid
from django.core.files.storage import default_storage
from django.utils import timezone
from .models import Document, DocumentPage, DocumentExtraction, DocumentEmbedding
import logging

logger = logging.getLogger(__name__)


class DocumentService:
    """Service for document operations."""

    @staticmethod
    def upload_document(organization, uploaded_by, file, name=None, description='',
                       file_type=None, extract_text=True, generate_embeddings=False):
        """
        Upload and process a document.

        Args:
            organization: Organization instance
            uploaded_by: User instance
            file: Uploaded file
            name: Document name (optional)
            description: Document description
            file_type: File type (optional, auto-detected)
            extract_text: Whether to extract text
            generate_embeddings: Whether to generate embeddings

        Returns:
            Document instance
        """
        # Determine file properties
        file_name = name or file.name
        file_ext = file.name.split('.')[-1].lower()
        mime_type = file.content_type

        # Auto-detect file type
        if not file_type:
            file_type = DocumentService._detect_file_type(file_ext, mime_type)

        # Generate unique file path
        file_path = f'documents/{organization.id}/{uuid.uuid4()}.{file_ext}'

        # Save file
        saved_path = default_storage.save(file_path, file)

        # Create document record
        document = Document.objects.create(
            organization=organization,
            uploaded_by=uploaded_by,
            name=file_name,
            description=description,
            file_path=saved_path,
            file_size=file.size,
            file_type=file_type,
            mime_type=mime_type,
            status='processing'
        )

        # Trigger async processing
        if extract_text or generate_embeddings:
            from .tasks import process_document
            process_document.delay(str(document.id), extract_text, generate_embeddings)

        return document

    @staticmethod
    def _detect_file_type(file_ext, mime_type):
        """Detect file type from extension and MIME type."""
        type_map = {
            'pdf': 'pdf',
            'doc': 'document',
            'docx': 'document',
            'xls': 'spreadsheet',
            'xlsx': 'spreadsheet',
            'csv': 'spreadsheet',
            'png': 'image',
            'jpg': 'image',
            'jpeg': 'image',
            'gif': 'image',
        }
        return type_map.get(file_ext, 'other')

    @staticmethod
    def search_documents(organization, query, search_type='text', file_type=None, limit=10):
        """
        Search documents.

        Args:
            organization: Organization instance
            query: Search query
            search_type: 'text' or 'semantic'
            file_type: Filter by file type
            limit: Maximum results

        Returns:
            List of document dictionaries
        """
        from django.db.models import Q

        documents = Document.objects.filter(organization=organization)

        if file_type:
            documents = documents.filter(file_type=file_type)

        if search_type == 'text':
            # Text search
            documents = documents.filter(
                Q(name__icontains=query) |
                Q(description__icontains=query) |
                Q(pages__text_content__icontains=query)
            ).distinct()
        else:
            # Semantic search (requires embeddings)
            # TODO: Implement semantic search using pgvector
            documents = documents.filter(
                embeddings__chunk_text__icontains=query
            ).distinct()

        documents = documents[:limit]

        return [
            {
                'id': str(doc.id),
                'name': doc.name,
                'file_type': doc.file_type,
                'created_at': doc.created_at.isoformat()
            }
            for doc in documents
        ]

    @staticmethod
    def get_download_url(document):
        """
        Get download URL for document.

        Args:
            document: Document instance

        Returns:
            Download URL string
        """
        # Generate presigned URL for S3 or return local path
        try:
            from django.conf import settings
            if settings.DEFAULT_FILE_STORAGE == 'storages.backends.s3boto3.S3Boto3Storage':
                # Generate S3 presigned URL
                url = default_storage.url(document.file_path)
                return url
            else:
                # Local file URL
                return default_storage.url(document.file_path)
        except Exception as e:
            logger.error(f'Failed to generate download URL: {str(e)}')
            raise
