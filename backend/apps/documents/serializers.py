"""
Serializers for Documents app.
"""
from rest_framework import serializers
from .models import Document, DocumentPage, DocumentExtraction, DocumentEmbedding


class DocumentPageSerializer(serializers.ModelSerializer):
    """Serializer for DocumentPage model."""

    class Meta:
        model = DocumentPage
        fields = [
            'id', 'document', 'page_number', 'text_content',
            'ocr_confidence', 'metadata', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class DocumentExtractionSerializer(serializers.ModelSerializer):
    """Serializer for DocumentExtraction model."""

    class Meta:
        model = DocumentExtraction
        fields = [
            'id', 'document', 'extraction_type', 'structured_data',
            'confidence_score', 'extracted_by', 'metadata', 'created_at'
        ]
        read_only_fields = ['id', 'extracted_by', 'created_at']


class DocumentEmbeddingSerializer(serializers.ModelSerializer):
    """Serializer for DocumentEmbedding model."""

    class Meta:
        model = DocumentEmbedding
        fields = [
            'id', 'document', 'chunk_index', 'chunk_text',
            'embedding_model', 'metadata', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class DocumentSerializer(serializers.ModelSerializer):
    """Serializer for Document model."""

    pages = DocumentPageSerializer(many=True, read_only=True)
    extractions = DocumentExtractionSerializer(many=True, read_only=True)
    uploaded_by_email = serializers.EmailField(source='uploaded_by.email', read_only=True)
    file_size_display = serializers.SerializerMethodField()

    class Meta:
        model = Document
        fields = [
            'id', 'organization', 'name', 'description', 'file_path',
            'file_size', 'file_size_display', 'file_type', 'mime_type',
            'status', 'uploaded_by', 'uploaded_by_email', 'page_count',
            'metadata', 'pages', 'extractions',
            'created_at', 'updated_at', 'processed_at'
        ]
        read_only_fields = [
            'id', 'organization', 'file_path', 'file_size', 'mime_type',
            'status', 'uploaded_by', 'page_count', 'processed_at',
            'created_at', 'updated_at'
        ]

    def get_file_size_display(self, obj):
        """Return human-readable file size."""
        size = obj.file_size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f'{size:.2f} {unit}'
            size /= 1024.0
        return f'{size:.2f} TB'


class DocumentUploadSerializer(serializers.Serializer):
    """Serializer for document upload."""

    file = serializers.FileField(help_text='Document file to upload')
    name = serializers.CharField(max_length=255, required=False, help_text='Document name (defaults to filename)')
    description = serializers.CharField(required=False, allow_blank=True)
    file_type = serializers.ChoiceField(
        choices=[choice[0] for choice in Document.FILE_TYPE_CHOICES],
        required=False,
        help_text='File type (auto-detected if not provided)'
    )
    extract_text = serializers.BooleanField(default=True, help_text='Whether to extract text using OCR')
    generate_embeddings = serializers.BooleanField(default=False, help_text='Whether to generate embeddings')

    def validate_file(self, value):
        """Validate uploaded file."""
        # Check file size (max 50MB)
        max_size = 50 * 1024 * 1024  # 50MB
        if value.size > max_size:
            raise serializers.ValidationError(f'File size cannot exceed {max_size // (1024 * 1024)}MB.')

        # Check file type
        allowed_types = ['pdf', 'docx', 'xlsx', 'csv', 'png', 'jpg', 'jpeg']
        file_ext = value.name.split('.')[-1].lower()
        if file_ext not in allowed_types:
            raise serializers.ValidationError(f'File type .{file_ext} is not supported. Allowed types: {", ".join(allowed_types)}')

        return value


class DocumentExtractionRequestSerializer(serializers.Serializer):
    """Serializer for requesting document extraction."""

    extraction_type = serializers.ChoiceField(
        choices=[choice[0] for choice in DocumentExtraction.EXTRACTION_TYPE_CHOICES],
        help_text='Type of extraction to perform'
    )
    extraction_config = serializers.JSONField(
        required=False,
        help_text='Configuration for extraction (e.g., entity types, schema)'
    )


class DocumentSearchSerializer(serializers.Serializer):
    """Serializer for document search."""

    query = serializers.CharField(help_text='Search query')
    search_type = serializers.ChoiceField(
        choices=['text', 'semantic'],
        default='text',
        help_text='Type of search (text or semantic)'
    )
    file_type = serializers.ChoiceField(
        choices=[choice[0] for choice in Document.FILE_TYPE_CHOICES],
        required=False,
        help_text='Filter by file type'
    )
    limit = serializers.IntegerField(default=10, min_value=1, max_value=100)
