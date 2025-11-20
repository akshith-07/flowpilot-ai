"""Services for AI Engine app."""
import logging
import hashlib
from django.utils import timezone
from datetime import timedelta

logger = logging.getLogger(__name__)


class AIService:
    """Service for AI operations."""

    @staticmethod
    def execute_ai_node(node, context, execution, step):
        """
        Execute an AI node using Gemini API.

        Args:
            node: Node definition
            context: Execution context
            execution: WorkflowExecution instance
            step: ExecutionStep instance

        Returns:
            dict: Node output
        """
        from apps.executions.models import AIRequest

        node_type = node.get('type', '')
        config = node.get('config', {})

        # Get prompt
        prompt = config.get('prompt', '')
        system_prompt = config.get('system_prompt', '')
        model = config.get('model', 'gemini-1.5-pro')

        # Check semantic cache
        cache_result = AIService._check_cache(prompt, model)
        if cache_result:
            logger.info('Using cached AI response')
            return {'output': cache_result, 'cached': True}

        try:
            # Call Gemini API (simplified)
            import google.generativeai as genai
            from django.conf import settings

            genai.configure(api_key=settings.GOOGLE_GEMINI_API_KEY)

            model_instance = genai.GenerativeModel(model)
            response = model_instance.generate_content(prompt)

            # Track AI request
            ai_request = AIRequest.objects.create(
                execution=execution,
                step=step,
                provider='gemini',
                model=model,
                prompt=prompt,
                response=response.text,
                system_prompt=system_prompt,
                input_tokens=len(prompt.split()),  # Simplified token count
                output_tokens=len(response.text.split()),
                success=True
            )

            # Update execution AI usage
            execution.ai_tokens_used += ai_request.total_tokens
            execution.save(update_fields=['ai_tokens_used', 'updated_at'])

            # Cache result
            AIService._cache_response(prompt, model, response.text)

            return {'output': response.text, 'cached': False}

        except Exception as e:
            logger.error(f'AI execution failed: {str(e)}')

            # Track failed request
            AIRequest.objects.create(
                execution=execution,
                step=step,
                provider='gemini',
                model=model,
                prompt=prompt,
                system_prompt=system_prompt,
                success=False,
                error_message=str(e)
            )

            raise

    @staticmethod
    def _check_cache(prompt, model):
        """Check semantic cache for similar prompts."""
        from apps.ai_engine.models import SemanticCache

        prompt_hash = hashlib.sha256(prompt.encode()).hexdigest()

        try:
            cache = SemanticCache.objects.get(
                prompt_hash=prompt_hash,
                model=model,
                expires_at__gt=timezone.now()
            )

            # Update hit count
            cache.hit_count += 1
            cache.last_hit_at = timezone.now()
            cache.save(update_fields=['hit_count', 'last_hit_at'])

            return cache.response

        except SemanticCache.DoesNotExist:
            return None

    @staticmethod
    def _cache_response(prompt, model, response, ttl_hours=24):
        """Cache AI response."""
        from apps.ai_engine.models import SemanticCache

        prompt_hash = hashlib.sha256(prompt.encode()).hexdigest()

        SemanticCache.objects.create(
            prompt_hash=prompt_hash,
            prompt=prompt,
            response=response,
            model=model,
            expires_at=timezone.now() + timedelta(hours=ttl_hours)
        )
