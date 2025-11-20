"""
API viewsets for AI Engine app.
"""
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from core.exceptions import ValidationError
from core.permissions import IsOrganizationMember
from .models import PromptTemplate
from .serializers import (
    PromptTemplateSerializer, AIRequestSerializer,
    AIExtractionRequestSerializer, AISummarizationRequestSerializer,
    AIClassificationRequestSerializer
)
from .services import AIService
import logging

logger = logging.getLogger(__name__)


class PromptTemplateViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing prompt templates.

    list: GET /api/v1/ai-engine/templates/
    create: POST /api/v1/ai-engine/templates/
    retrieve: GET /api/v1/ai-engine/templates/{id}/
    update: PUT/PATCH /api/v1/ai-engine/templates/{id}/
    destroy: DELETE /api/v1/ai-engine/templates/{id}/
    """

    serializer_class = PromptTemplateSerializer
    permission_classes = [permissions.IsAuthenticated, IsOrganizationMember]
    filterset_fields = ['category', 'is_active']
    search_fields = ['name', 'description']
    ordering = ['-created_at']

    def get_queryset(self):
        """Filter templates by organization."""
        if not self.request.organization:
            return PromptTemplate.objects.none()

        return PromptTemplate.objects.filter(
            organization=self.request.organization
        )

    def perform_create(self, serializer):
        """Set organization on create."""
        serializer.save(organization=self.request.organization)


class AIEngineViewSet(viewsets.GenericViewSet):
    """
    ViewSet for AI operations.
    """

    permission_classes = [permissions.IsAuthenticated, IsOrganizationMember]

    @action(detail=False, methods=['post'])
    def generate(self, request):
        """
        Generate text using AI.

        POST /api/v1/ai-engine/generate/
        """
        serializer = AIRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            result = AIService.generate_text(
                prompt=serializer.validated_data['prompt'],
                model=serializer.validated_data.get('model', 'gemini-pro'),
                temperature=serializer.validated_data.get('temperature', 0.7),
                max_tokens=serializer.validated_data.get('max_tokens', 1024),
                system_prompt=serializer.validated_data.get('system_prompt')
            )

            return Response({
                'success': True,
                'data': result
            })

        except Exception as e:
            logger.error(f'AI generation failed: {str(e)}')
            raise ValidationError(f'AI generation failed: {str(e)}')

    @action(detail=False, methods=['post'])
    def extract(self, request):
        """
        Extract structured data from text using AI.

        POST /api/v1/ai-engine/extract/
        """
        serializer = AIExtractionRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            result = AIService.extract_data(
                text=serializer.validated_data['text'],
                schema=serializer.validated_data['schema'],
                model=serializer.validated_data.get('model', 'gemini-pro')
            )

            return Response({
                'success': True,
                'data': result
            })

        except Exception as e:
            logger.error(f'AI extraction failed: {str(e)}')
            raise ValidationError(f'AI extraction failed: {str(e)}')

    @action(detail=False, methods=['post'])
    def summarize(self, request):
        """
        Summarize text using AI.

        POST /api/v1/ai-engine/summarize/
        """
        serializer = AISummarizationRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            result = AIService.summarize_text(
                text=serializer.validated_data['text'],
                max_length=serializer.validated_data.get('max_length', 200),
                style=serializer.validated_data.get('style', 'brief')
            )

            return Response({
                'success': True,
                'data': result
            })

        except Exception as e:
            logger.error(f'AI summarization failed: {str(e)}')
            raise ValidationError(f'AI summarization failed: {str(e)}')

    @action(detail=False, methods=['post'])
    def classify(self, request):
        """
        Classify text using AI.

        POST /api/v1/ai-engine/classify/
        """
        serializer = AIClassificationRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            result = AIService.classify_text(
                text=serializer.validated_data['text'],
                categories=serializer.validated_data['categories'],
                multi_label=serializer.validated_data.get('multi_label', False)
            )

            return Response({
                'success': True,
                'data': result
            })

        except Exception as e:
            logger.error(f'AI classification failed: {str(e)}')
            raise ValidationError(f'AI classification failed: {str(e)}')
