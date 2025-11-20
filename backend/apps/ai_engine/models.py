"""
AI Engine models for FlowPilot AI.
Handles Gemini API integration and prompt management.
"""
import uuid
from django.db import models
from apps.organizations.models import Organization


class PromptTemplate(models.Model):
    """Reusable prompt templates."""

    CATEGORY_CHOICES = [
        ('summarization', 'Summarization'),
        ('extraction', 'Extraction'),
        ('classification', 'Classification'),
        ('generation', 'Generation'),
        ('translation', 'Translation'),
        ('other', 'Other'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='prompt_templates', null=True, blank=True)
    name = models.CharField(max_length=255)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    template = models.TextField()  # Jinja2 template
    system_prompt = models.TextField(null=True, blank=True)
    parameters = models.JSONField(default=dict, blank=True)  # Template parameters
    is_public = models.BooleanField(default=False)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'prompt_templates'
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class SemanticCache(models.Model):
    """Cache for similar prompts to reduce API calls."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    prompt_hash = models.CharField(max_length=64, db_index=True)  # SHA256 of prompt
    prompt = models.TextField()
    response = models.TextField()
    model = models.CharField(max_length=100)
    embedding_vector = models.JSONField(null=True, blank=True)  # For semantic similarity
    hit_count = models.IntegerField(default=0)
    last_hit_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'semantic_cache'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['prompt_hash']),
            models.Index(fields=['expires_at']),
        ]
