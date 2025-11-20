"""
Celery tasks for Executions app.
"""
from celery import shared_task
from django.utils import timezone
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)


@shared_task
def cleanup_old_executions(days=90):
    """
    Cleanup old completed executions.

    Args:
        days: Number of days to keep executions

    Returns:
        dict: Number of executions deleted
    """
    from .models import WorkflowExecution

    cutoff_date = timezone.now() - timedelta(days=days)
    deleted_count, _ = WorkflowExecution.objects.filter(
        status__in=['completed', 'failed', 'cancelled'],
        created_at__lt=cutoff_date
    ).delete()

    logger.info(f'Deleted {deleted_count} old executions')
    return {'deleted_count': deleted_count}


@shared_task
def cleanup_old_execution_logs(days=30):
    """
    Cleanup old execution logs.

    Args:
        days: Number of days to keep logs

    Returns:
        dict: Number of logs deleted
    """
    from .models import ExecutionLog

    cutoff_date = timezone.now() - timedelta(days=days)
    deleted_count, _ = ExecutionLog.objects.filter(
        created_at__lt=cutoff_date
    ).delete()

    logger.info(f'Deleted {deleted_count} old execution logs')
    return {'deleted_count': deleted_count}


@shared_task
def calculate_ai_costs():
    """Calculate and update AI costs for executions."""
    from .models import AIRequest, WorkflowExecution

    # Update execution AI costs
    executions = WorkflowExecution.objects.filter(
        status='completed',
        ai_cost=0
    )

    updated_count = 0
    for execution in executions:
        total_cost = sum(
            request.cost for request in execution.ai_requests.all()
        )
        total_tokens = sum(
            request.total_tokens for request in execution.ai_requests.all()
        )

        execution.ai_cost = total_cost
        execution.ai_tokens_used = total_tokens
        execution.save(update_fields=['ai_cost', 'ai_tokens_used', 'updated_at'])
        updated_count += 1

    logger.info(f'Updated AI costs for {updated_count} executions')
    return {'updated_count': updated_count}
