"""
Celery tasks for Workflows app.
"""
from celery import shared_task
from django.utils import timezone
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)


@shared_task
def execute_scheduled_workflows():
    """
    Execute workflows with scheduled triggers.
    This task should run every minute via Celery Beat.

    Returns:
        dict: Number of workflows executed
    """
    from .models import WorkflowTrigger
    from apps.executions.services import ExecutionService

    now = timezone.now()
    executed_count = 0

    # Get active scheduled triggers
    scheduled_triggers = WorkflowTrigger.objects.filter(
        trigger_type='scheduled',
        is_active=True,
        workflow__is_active=True
    ).select_related('workflow')

    for trigger in scheduled_triggers:
        try:
            # Check if trigger should execute based on cron expression
            from croniter import croniter

            if not trigger.cron_expression:
                continue

            cron = croniter(trigger.cron_expression, now)

            # Check if trigger should execute in the next minute
            next_run = cron.get_next(timezone.datetime)
            if next_run <= (now + timedelta(minutes=1)):
                # Execute workflow
                ExecutionService.execute_workflow(
                    workflow=trigger.workflow,
                    input_data={},
                    triggered_by=None,
                    trigger=trigger
                )

                trigger.increment_execution_count()
                executed_count += 1

                logger.info(
                    f'Executed scheduled workflow: {trigger.workflow.name}'
                )

        except Exception as e:
            logger.error(
                f'Error executing scheduled workflow {trigger.workflow.name}: {str(e)}'
            )

    return {'executed_count': executed_count}


@shared_task
def cleanup_old_workflow_versions(days=90):
    """
    Cleanup old workflow versions (keep latest N versions).

    Args:
        days: Number of days to keep versions

    Returns:
        dict: Number of versions deleted
    """
    from .models import WorkflowVersion, Workflow

    cutoff_date = timezone.now() - timedelta(days=days)
    deleted_count = 0

    # For each workflow, keep only the latest 10 versions
    workflows = Workflow.objects.all()

    for workflow in workflows:
        # Get versions older than cutoff date
        old_versions = workflow.versions.filter(
            created_at__lt=cutoff_date
        ).order_by('-version_number')

        # Keep latest 10 versions, delete the rest
        versions_to_delete = old_versions[10:]

        for version in versions_to_delete:
            # Don't delete current version
            if workflow.current_version and version.id == workflow.current_version.id:
                continue

            version.delete()
            deleted_count += 1

    logger.info(f'Deleted {deleted_count} old workflow versions')
    return {'deleted_count': deleted_count}


@shared_task
def update_workflow_statistics():
    """
    Update workflow statistics (execution counts, success rates, etc.).

    Returns:
        dict: Number of workflows updated
    """
    from .models import Workflow
    from apps.executions.models import WorkflowExecution

    updated_count = 0

    workflows = Workflow.objects.all()

    for workflow in workflows:
        # Get execution statistics
        executions = WorkflowExecution.objects.filter(workflow=workflow)

        total_count = executions.count()
        success_count = executions.filter(status='completed').count()
        failure_count = executions.filter(status='failed').count()

        # Get last executed time
        last_execution = executions.order_by('-created_at').first()
        last_executed_at = last_execution.created_at if last_execution else None

        # Update workflow
        workflow.execution_count = total_count
        workflow.success_count = success_count
        workflow.failure_count = failure_count
        workflow.last_executed_at = last_executed_at
        workflow.save(update_fields=[
            'execution_count', 'success_count', 'failure_count',
            'last_executed_at', 'updated_at'
        ])

        updated_count += 1

    logger.info(f'Updated statistics for {updated_count} workflows')
    return {'updated_count': updated_count}


@shared_task(bind=True, max_retries=3)
def validate_workflow_definition(self, workflow_id):
    """
    Validate workflow definition and report errors.

    Args:
        workflow_id: UUID of the workflow

    Returns:
        dict: Validation result
    """
    from .models import Workflow
    from .services import WorkflowService

    try:
        workflow = Workflow.objects.get(id=workflow_id)

        # Validate definition
        errors = WorkflowService.validate_workflow_definition(workflow.definition)

        if errors:
            logger.warning(
                f'Workflow {workflow.name} has validation errors: {errors}'
            )

            # Send notification to workflow owner
            from apps.notifications.services import NotificationService
            NotificationService.send_notification(
                organization=workflow.organization,
                title=f'Workflow validation errors: {workflow.name}',
                message=f'Found {len(errors)} validation errors in workflow definition',
                notification_type='warning',
                metadata={
                    'workflow_id': str(workflow.id),
                    'errors': errors
                }
            )

        return {
            'workflow_id': str(workflow.id),
            'valid': len(errors) == 0,
            'errors': errors
        }

    except Workflow.DoesNotExist:
        logger.error(f'Workflow {workflow_id} not found')
        return {'status': 'error', 'message': 'Workflow not found'}

    except Exception as exc:
        logger.error(f'Error validating workflow: {str(exc)}')
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))


@shared_task
def generate_workflow_report(workflow_id):
    """
    Generate comprehensive workflow report.

    Args:
        workflow_id: UUID of the workflow

    Returns:
        dict: Report data
    """
    from .models import Workflow
    from .services import WorkflowService

    try:
        workflow = Workflow.objects.get(id=workflow_id)

        # Get statistics
        stats = WorkflowService.get_workflow_statistics(workflow)

        # Get dependencies
        dependencies = WorkflowService.get_workflow_dependencies(workflow)

        # Compile report
        report = {
            'workflow': {
                'id': str(workflow.id),
                'name': workflow.name,
                'status': workflow.status,
                'version': workflow.version,
            },
            'statistics': stats,
            'dependencies': dependencies,
            'generated_at': timezone.now().isoformat(),
        }

        logger.info(f'Generated report for workflow: {workflow.name}')
        return report

    except Workflow.DoesNotExist:
        logger.error(f'Workflow {workflow_id} not found')
        return {'status': 'error', 'message': 'Workflow not found'}


@shared_task
def auto_pause_failing_workflows(failure_threshold=10, failure_rate=0.8):
    """
    Automatically pause workflows with high failure rates.

    Args:
        failure_threshold: Minimum executions before checking
        failure_rate: Failure rate threshold (0-1)

    Returns:
        dict: Number of workflows paused
    """
    from .models import Workflow

    paused_count = 0

    # Get active workflows with sufficient executions
    workflows = Workflow.objects.filter(
        is_active=True,
        execution_count__gte=failure_threshold
    )

    for workflow in workflows:
        # Calculate failure rate
        if workflow.execution_count > 0:
            current_failure_rate = workflow.failure_count / workflow.execution_count

            if current_failure_rate >= failure_rate:
                # Pause workflow
                workflow.is_active = False
                workflow.status = 'paused'
                workflow.save(update_fields=['is_active', 'status', 'updated_at'])

                paused_count += 1

                # Send notification
                from apps.notifications.services import NotificationService
                NotificationService.send_notification(
                    organization=workflow.organization,
                    title=f'Workflow auto-paused: {workflow.name}',
                    message=(
                        f'Workflow has been automatically paused due to high failure rate '
                        f'({current_failure_rate*100:.1f}%). '
                        f'Please review and fix the workflow.'
                    ),
                    notification_type='warning',
                    metadata={'workflow_id': str(workflow.id)}
                )

                logger.warning(
                    f'Auto-paused workflow {workflow.name} '
                    f'(failure rate: {current_failure_rate*100:.1f}%)'
                )

    return {'paused_count': paused_count}
