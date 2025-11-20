"""Django admin for Documents app."""
from django.contrib import admin
from .models import Document, DocumentPage, DocumentExtraction, DocumentEmbedding

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ['name', 'organization', 'mime_type', 'file_size', 'uploaded_by', 'created_at']
    list_filter = ['mime_type', 'created_at']
    search_fields = ['name', 'organization__name']

@admin.register(DocumentPage)
class DocumentPageAdmin(admin.ModelAdmin):
    list_display = ['document', 'page_number', 'ocr_confidence', 'created_at']

@admin.register(DocumentExtraction)
class DocumentExtractionAdmin(admin.ModelAdmin):
    list_display = ['document', 'extraction_type', 'confidence', 'created_at']
    list_filter = ['extraction_type']

@admin.register(DocumentEmbedding)
class DocumentEmbeddingAdmin(admin.ModelAdmin):
    list_display = ['document', 'chunk_number', 'created_at']
