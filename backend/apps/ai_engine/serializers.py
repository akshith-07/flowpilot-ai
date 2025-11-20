"""
Serializers for AI Engine app.
"""
from rest_framework import serializers
from .models import PromptTemplate, SemanticCache


class PromptTemplateSerializer(serializers.ModelSerializer):
    """Serializer for PromptTemplate model."""

    class Meta:
        model = PromptTemplate
        fields = [
            'id', 'organization', 'name', 'description', 'template_text',
            'variables', 'category', 'is_active', 'metadata',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'organization', 'created_at', 'updated_at']


class SemanticCacheSerializer(serializers.ModelSerializer):
    """Serializer for SemanticCache model."""

    class Meta:
        model = SemanticCache
        fields = [
            'id', 'prompt_hash', 'response', 'model_name',
            'tokens_used', 'created_at', 'expires_at'
        ]
        read_only_fields = ['id', 'created_at']


class AIRequestSerializer(serializers.Serializer):
    """Serializer for AI request."""

    prompt = serializers.CharField(help_text='Prompt text')
    model = serializers.ChoiceField(
        choices=['gemini-pro', 'gemini-flash'],
        default='gemini-pro',
        help_text='AI model to use'
    )
    temperature = serializers.FloatField(default=0.7, min_value=0.0, max_value=2.0)
    max_tokens = serializers.IntegerField(default=1024, min_value=1, max_value=8192)
    system_prompt = serializers.CharField(required=False, allow_blank=True)


class AIExtractionRequestSerializer(serializers.Serializer):
    """Serializer for AI data extraction request."""

    text = serializers.CharField(help_text='Text to extract data from')
    schema = serializers.JSONField(help_text='JSON schema for extraction')
    model = serializers.ChoiceField(
        choices=['gemini-pro', 'gemini-flash'],
        default='gemini-pro'
    )


class AISummarizationRequestSerializer(serializers.Serializer):
    """Serializer for AI summarization request."""

    text = serializers.CharField(help_text='Text to summarize')
    max_length = serializers.IntegerField(default=200, min_value=50, max_value=1000)
    style = serializers.ChoiceField(
        choices=['brief', 'detailed', 'bullet_points'],
        default='brief'
    )


class AIClassificationRequestSerializer(serializers.Serializer):
    """Serializer for AI classification request."""

    text = serializers.CharField(help_text='Text to classify')
    categories = serializers.ListField(
        child=serializers.CharField(),
        help_text='List of possible categories'
    )
    multi_label = serializers.BooleanField(default=False)
