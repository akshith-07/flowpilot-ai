"""
Document models for FlowPilot AI.
Handles document upload, OCR, and extraction.
"""
import uuid
from django.db import models
from django.contrib.auth import get_user_model
from apps.organizations.models import Organization

User = get_user_model()


class Document(models.Model):
    """Document storage and metadata."""

    MIME_TYPE_CHOICES = [
        ('application/pdf', 'PDF'),
        ('application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'DOCX'),
        ('application/vnd.ms-excel', 'Excel'),
        ('text/csv', 'CSV'),
        ('image/png', 'PNG'),
        ('image/jpeg', 'JPEG'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='documents')
    name = models.CharField(max_length=255)
    file_path = models.CharField(max_length=500)
    file_size = models.BigIntegerField()  # in bytes
    mime_type = models.CharField(max_length=100)
    checksum = models.CharField(max_length=64)  # SHA256
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='uploaded_documents')
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'documents'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['organization', '-created_at']),
        ]

    def __str__(self):
        return self.name


class DocumentPage(models.Model):
    """Individual pages of documents."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='pages')
    page_number = models.IntegerField()
    text_content = models.TextField(null=True, blank=True)
    ocr_confidence = models.FloatField(null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'document_pages'
        ordering = ['document', 'page_number']
        unique_together = [['document', 'page_number']]


class DocumentExtraction(models.Model):
    """Extracted data from documents."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='extractions')
    extraction_type = models.CharField(max_length=100)  # entities, tables, key_value, etc.
    structured_data = models.JSONField(default=dict)
    confidence = models.FloatField(null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'document_extractions'
        ordering = ['-created_at']


class DocumentEmbedding(models.Model):
    """Vector embeddings for semantic search."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='embeddings')
    chunk_text = models.TextField()
    chunk_number = models.IntegerField()
    embedding_vector = models.JSONField()  # Store as list of floats
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'document_embeddings'
        ordering = ['document', 'chunk_number']
