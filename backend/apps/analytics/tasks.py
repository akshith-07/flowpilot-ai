"""
Celery tasks for Analytics app.
"""
from celery import shared_task
from django.db.models import Sum
from django.utils import timezone
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True)
def aggregate_daily_metrics(self):
    """
    Aggregate daily metrics for all organizations.
    Runs daily at midnight.
    """
    try:
        from .models import DailyMetrics
        from apps.organizations.models import Organization
        from apps.users.models import User
        from apps.workflows.models import Workflow
        from apps.executions.models import WorkflowExecution, AIRequest
        from apps.documents.models import Document

        yesterday = (timezone.now() - timedelta(days=1)).date()

        for org in Organization.objects.filter(is_active=True):
            try:
                # Count active users (users who performed any action yesterday)
                active_users = User.objects.filter(
                    organizations__organization=org,
                    user_activities__created_at__date=yesterday
                ).distinct().count()

                # Count workflow executions
                executions = WorkflowExecution.objects.filter(
                    workflow__organization=org,
                    created_at__date=yesterday
                )
                total_executions = executions.count()
                successful = executions.filter(status='completed').count()
                failed = executions.filter(status='failed').count()

                # Count AI requests
                ai_requests = AIRequest.objects.filter(
                    organization=org,
                    created_at__date=yesterday
                )
                total_ai_requests = ai_requests.count()
                total_tokens = ai_requests.aggregate(Sum('tokens_used'))['tokens_used__sum'] or 0
                total_ai_cost = ai_requests.aggregate(Sum('cost'))['cost__sum'] or 0

                # Count documents processed
                documents_processed = Document.objects.filter(
                    organization=org,
                    processed_at__date=yesterday
                ).count()

                # Create or update daily metrics
                DailyMetrics.objects.update_or_create(
                    organization=org,
                    date=yesterday,
                    defaults={
                        'active_users': active_users,
                        'workflow_executions': total_executions,
                        'successful_executions': successful,
                        'failed_executions': failed,
                        'ai_requests': total_ai_requests,
                        'ai_tokens_used': total_tokens,
                        'ai_cost': total_ai_cost,
                        'documents_processed': documents_processed,
                        'storage_used_bytes': 0  # TODO: Calculate actual storage
                    }
                )

                logger.info(f'Daily metrics aggregated for organization: {org.name}')

            except Exception as e:
                logger.error(f'Failed to aggregate metrics for {org.name}: {str(e)}')

    except Exception as e:
        logger.error(f'Failed to aggregate daily metrics: {str(e)}')
