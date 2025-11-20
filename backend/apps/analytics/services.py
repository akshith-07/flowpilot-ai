"""
Business logic services for Analytics app.
"""
from django.db.models import Count, Avg, Sum, Q
from django.utils import timezone
from datetime import timedelta
from .models import DailyMetrics, UserActivity, ErrorLog
import logging

logger = logging.getLogger(__name__)


class AnalyticsService:
    """Service for analytics operations."""

    @staticmethod
    def get_dashboard_metrics(organization, period='week'):
        """
        Get dashboard metrics for organization.

        Args:
            organization: Organization instance
            period: Time period ('today', 'week', 'month', 'year')

        Returns:
            Dictionary with metrics
        """
        # Calculate date range
        end_date = timezone.now().date()

        if period == 'today':
            start_date = end_date
        elif period == 'week':
            start_date = end_date - timedelta(days=7)
        elif period == 'month':
            start_date = end_date - timedelta(days=30)
        elif period == 'year':
            start_date = end_date - timedelta(days=365)
        else:
            start_date = end_date - timedelta(days=7)

        # Aggregate metrics
        metrics = DailyMetrics.objects.filter(
            organization=organization,
            date__gte=start_date,
            date__lte=end_date
        ).aggregate(
            total_active_users=Sum('active_users'),
            total_executions=Sum('workflow_executions'),
            successful_executions=Sum('successful_executions'),
            failed_executions=Sum('failed_executions'),
            total_ai_requests=Sum('ai_requests'),
            total_ai_cost=Sum('ai_cost'),
            total_documents=Sum('documents_processed')
        )

        # Calculate success rate
        total_executions = metrics['total_executions'] or 0
        successful = metrics['successful_executions'] or 0
        success_rate = (successful / total_executions * 100) if total_executions > 0 else 0

        # Count total workflows
        from apps.workflows.models import Workflow
        total_workflows = Workflow.objects.filter(
            organization=organization,
            is_active=True
        ).count()

        return {
            'period': period,
            'active_users': metrics['total_active_users'] or 0,
            'total_workflows': total_workflows,
            'total_executions': total_executions,
            'success_rate': round(success_rate, 2),
            'ai_requests': metrics['total_ai_requests'] or 0,
            'ai_cost': float(metrics['total_ai_cost'] or 0),
            'documents_processed': metrics['total_documents'] or 0
        }

    @staticmethod
    def get_workflow_analytics(organization):
        """Get analytics for workflows."""
        from apps.workflows.models import Workflow
        from apps.executions.models import WorkflowExecution
        from django.db.models import F, ExpressionWrapper, DurationField

        workflows = Workflow.objects.filter(organization=organization, is_active=True)

        analytics = []
        for workflow in workflows:
            executions = WorkflowExecution.objects.filter(workflow=workflow)

            analytics.append({
                'workflow_id': str(workflow.id),
                'workflow_name': workflow.name,
                'execution_count': executions.count(),
                'success_count': executions.filter(status='completed').count(),
                'failure_count': executions.filter(status='failed').count(),
                'average_duration': 0,  # Calculate from execution timestamps
                'total_ai_cost': float(executions.aggregate(Sum('ai_cost'))['ai_cost__sum'] or 0)
            })

        return analytics

    @staticmethod
    def get_ai_usage_analytics(organization):
        """Get AI usage analytics."""
        from apps.executions.models import AIRequest

        # Get AI requests for the organization
        ai_requests = AIRequest.objects.filter(organization=organization)

        # Aggregate by date
        daily_usage = ai_requests.extra(
            select={'day': 'DATE(created_at)'}
        ).values('day').annotate(
            total_requests=Count('id'),
            total_tokens=Sum('tokens_used'),
            total_cost=Sum('cost')
        ).order_by('-day')[:30]

        return {
            'total_requests': ai_requests.count(),
            'total_tokens': ai_requests.aggregate(Sum('tokens_used'))['tokens_used__sum'] or 0,
            'total_cost': float(ai_requests.aggregate(Sum('cost'))['cost__sum'] or 0),
            'daily_usage': list(daily_usage)
        }

    @staticmethod
    def get_error_analytics(organization):
        """Get error analytics."""
        error_logs = ErrorLog.objects.filter(organization=organization)

        # Group by error type
        by_type = error_logs.values('error_type').annotate(
            count=Count('id')
        ).order_by('-count')[:10]

        # Recent errors
        recent_errors = ErrorLog.objects.filter(
            organization=organization,
            resolved=False
        ).order_by('-created_at')[:10]

        return {
            'total_errors': error_logs.count(),
            'unresolved_errors': error_logs.filter(resolved=False).count(),
            'by_type': list(by_type),
            'recent_errors': [
                {
                    'id': str(err.id),
                    'error_type': err.error_type,
                    'message': err.error_message,
                    'severity': err.severity,
                    'created_at': err.created_at.isoformat()
                }
                for err in recent_errors
            ]
        }
