"""
ViewSets for Execution models.
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from .models import WorkflowExecution, ExecutionStep, ExecutionLog, AIRequest
from .serializers import (
    WorkflowExecutionSerializer, WorkflowExecutionListSerializer,
    ExecutionStepSerializer, ExecutionLogSerializer, AIRequestSerializer,
    ExecutionRetrySerializer
)
from apps.organizations.permissions import IsOrganizationMember


class WorkflowExecutionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for WorkflowExecution model.
    Read-only as executions are created via workflow execution endpoint.
    """
    permission_classes = [IsAuthenticated, IsOrganizationMember]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['workflow__name']
    ordering_fields = ['created_at', 'started_at', 'completed_at', 'duration']
    ordering = ['-created_at']
    filterset_fields = ['status', 'workflow']

    def get_queryset(self):
        """Get executions based on organization context."""
        organization_id = self.request.query_params.get('organization')
        if not organization_id:
            return WorkflowExecution.objects.none()

        return WorkflowExecution.objects.filter(
            workflow__organization_id=organization_id
        ).select_related('workflow', 'trigger', 'triggered_by').prefetch_related('steps', 'logs')

    def get_serializer_class(self):
        """Return appropriate serializer class."""
        if self.action == 'list':
            return WorkflowExecutionListSerializer
        return WorkflowExecutionSerializer

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel a running execution."""
        execution = self.get_object()

        if execution.status not in ['pending', 'running', 'paused']:
            return Response(
                {'error': 'Only pending, running, or paused executions can be cancelled'},
                status=status.HTTP_400_BAD_REQUEST
            )

        execution.cancel()

        return Response({
            'message': 'Execution cancelled successfully',
            'execution': WorkflowExecutionSerializer(execution).data
        })

    @action(detail=True, methods=['post'])
    def retry(self, request, pk=None):
        """Retry a failed execution."""
        execution = self.get_object()

        if not execution.can_retry():
            return Response(
                {'error': 'Execution cannot be retried (either not failed or max retries reached)'},
                status=status.HTTP_400_BAD_REQUEST
            )

        retry_execution = execution.create_retry(triggered_by=request.user)

        # Execute the retry
        from .services import ExecutionService
        ExecutionService.execute_workflow_async.delay(str(retry_execution.id))

        return Response(
            WorkflowExecutionSerializer(retry_execution).data,
            status=status.HTTP_201_CREATED
        )

    @action(detail=True, methods=['get'])
    def logs(self, request, pk=None):
        """Get execution logs."""
        execution = self.get_object()
        logs = execution.logs.all().order_by('created_at')

        serializer = ExecutionLogSerializer(logs, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def steps(self, request, pk=None):
        """Get execution steps."""
        execution = self.get_object()
        steps = execution.steps.all().order_by('step_number')

        serializer = ExecutionStepSerializer(steps, many=True)
        return Response(serializer.data)


class ExecutionStepViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for ExecutionStep model."""

    permission_classes = [IsAuthenticated, IsOrganizationMember]
    serializer_class = ExecutionStepSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    ordering_fields = ['step_number', 'created_at']
    ordering = ['step_number']
    filterset_fields = ['status', 'node_type']

    def get_queryset(self):
        """Get steps based on execution context."""
        execution_id = self.request.query_params.get('execution')
        if not execution_id:
            return ExecutionStep.objects.none()

        return ExecutionStep.objects.filter(
            execution_id=execution_id
        ).prefetch_related('logs', 'ai_requests')


class ExecutionLogViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for ExecutionLog model."""

    permission_classes = [IsAuthenticated, IsOrganizationMember]
    serializer_class = ExecutionLogSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    ordering_fields = ['created_at']
    ordering = ['created_at']
    filterset_fields = ['level']

    def get_queryset(self):
        """Get logs based on execution context."""
        execution_id = self.request.query_params.get('execution')
        if not execution_id:
            return ExecutionLog.objects.none()

        return ExecutionLog.objects.filter(execution_id=execution_id)


class AIRequestViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for AIRequest model."""

    permission_classes = [IsAuthenticated, IsOrganizationMember]
    serializer_class = AIRequestSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    ordering_fields = ['created_at', 'cost', 'total_tokens']
    ordering = ['-created_at']
    filterset_fields = ['provider', 'success']

    def get_queryset(self):
        """Get AI requests based on execution context."""
        execution_id = self.request.query_params.get('execution')
        if not execution_id:
            return AIRequest.objects.none()

        return AIRequest.objects.filter(execution_id=execution_id)
