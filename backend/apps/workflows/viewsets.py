"""
ViewSets for Workflow models.
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db import transaction
from django.shortcuts import get_object_or_404

from .models import (
    Workflow, WorkflowVersion, WorkflowTemplate,
    WorkflowVariable, WorkflowTrigger
)
from .serializers import (
    WorkflowSerializer, WorkflowListSerializer, WorkflowVersionSerializer,
    WorkflowTemplateSerializer, WorkflowTemplateListSerializer,
    WorkflowVariableSerializer, WorkflowTriggerSerializer,
    WorkflowTestSerializer, CreateVersionSerializer, RollbackVersionSerializer
)
from apps.organizations.permissions import IsOrganizationMember
from .services import WorkflowService


class WorkflowTemplateViewSet(viewsets.ModelViewSet):
    """
    ViewSet for WorkflowTemplate model.

    list: Get all public templates
    create: Create a new template
    retrieve: Get template details
    update: Update template
    partial_update: Partially update template
    destroy: Delete template
    """
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description', 'tags']
    ordering_fields = ['name', 'created_at', 'use_count']
    ordering = ['-is_featured', '-use_count']
    filterset_fields = ['category', 'is_public', 'is_featured']

    def get_queryset(self):
        """Get templates based on visibility."""
        if self.request.user.is_staff:
            return WorkflowTemplate.objects.all()

        return WorkflowTemplate.objects.filter(is_public=True)

    def get_serializer_class(self):
        """Return appropriate serializer class."""
        if self.action == 'list':
            return WorkflowTemplateListSerializer
        return WorkflowTemplateSerializer

    def perform_create(self, serializer):
        """Set created_by when creating template."""
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['post'])
    def use(self, request, pk=None):
        """
        Create a workflow from this template.
        """
        template = self.get_object()
        organization_id = request.data.get('organization')

        if not organization_id:
            return Response(
                {'error': 'Organization ID is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create workflow from template
        workflow = Workflow.objects.create(
            organization_id=organization_id,
            name=f'{template.name} (Copy)',
            description=template.description,
            definition=template.definition,
            template=template,
            created_by=request.user,
            updated_by=request.user
        )

        # Increment template use count
        template.increment_use_count()

        return Response(
            WorkflowSerializer(workflow).data,
            status=status.HTTP_201_CREATED
        )


class WorkflowViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Workflow model.

    list: Get all workflows for organization
    create: Create a new workflow
    retrieve: Get workflow details
    update: Update workflow
    partial_update: Partially update workflow
    destroy: Delete workflow
    """
    permission_classes = [IsAuthenticated, IsOrganizationMember]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description', 'tags']
    ordering_fields = ['name', 'created_at', 'updated_at', 'last_executed_at']
    ordering = ['-updated_at']
    filterset_fields = ['status', 'is_active', 'template']

    def get_queryset(self):
        """Get workflows based on organization context."""
        organization_id = self.request.query_params.get('organization')
        if not organization_id:
            return Workflow.objects.none()

        return Workflow.objects.filter(
            organization_id=organization_id
        ).select_related(
            'organization', 'template', 'created_by', 'updated_by'
        ).prefetch_related('variables', 'triggers', 'versions')

    def get_serializer_class(self):
        """Return appropriate serializer class."""
        if self.action == 'list':
            return WorkflowListSerializer
        return WorkflowSerializer

    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """Activate a workflow."""
        workflow = self.get_object()
        workflow.is_active = True
        workflow.status = 'active'
        workflow.save(update_fields=['is_active', 'status', 'updated_at'])

        return Response({
            'message': 'Workflow activated successfully',
            'workflow': WorkflowSerializer(workflow).data
        })

    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """Deactivate a workflow."""
        workflow = self.get_object()
        workflow.is_active = False
        workflow.status = 'paused'
        workflow.save(update_fields=['is_active', 'status', 'updated_at'])

        return Response({
            'message': 'Workflow deactivated successfully',
            'workflow': WorkflowSerializer(workflow).data
        })

    @action(detail=True, methods=['post'])
    def archive(self, request, pk=None):
        """Archive a workflow."""
        workflow = self.get_object()
        workflow.is_active = False
        workflow.status = 'archived'
        workflow.save(update_fields=['is_active', 'status', 'updated_at'])

        return Response({
            'message': 'Workflow archived successfully',
            'workflow': WorkflowSerializer(workflow).data
        })

    @action(detail=True, methods=['post'])
    def duplicate(self, request, pk=None):
        """Duplicate a workflow."""
        workflow = self.get_object()

        # Create a copy
        new_workflow = Workflow.objects.create(
            organization=workflow.organization,
            name=f'{workflow.name} (Copy)',
            description=workflow.description,
            definition=workflow.definition,
            template=workflow.template,
            tags=workflow.tags,
            metadata=workflow.metadata,
            created_by=request.user,
            updated_by=request.user
        )

        # Copy variables
        for variable in workflow.variables.all():
            WorkflowVariable.objects.create(
                workflow=new_workflow,
                name=variable.name,
                variable_type=variable.variable_type,
                scope=variable.scope,
                default_value=variable.default_value,
                is_required=variable.is_required,
                is_secret=variable.is_secret,
                description=variable.description
            )

        return Response(
            WorkflowSerializer(new_workflow).data,
            status=status.HTTP_201_CREATED
        )

    @action(detail=True, methods=['post'])
    def test(self, request, pk=None):
        """Test workflow execution with mock data."""
        workflow = self.get_object()
        serializer = WorkflowTestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        input_data = serializer.validated_data.get('input_data', {})
        dry_run = serializer.validated_data.get('dry_run', True)

        # Execute workflow test
        result = WorkflowService.test_workflow(
            workflow=workflow,
            input_data=input_data,
            dry_run=dry_run
        )

        return Response(result)

    @action(detail=True, methods=['post'])
    def execute(self, request, pk=None):
        """Execute workflow."""
        workflow = self.get_object()

        # Check if workflow is active
        if not workflow.is_active:
            return Response(
                {'error': 'Workflow is not active'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get input data
        input_data = request.data.get('input_data', {})

        # Execute workflow
        from apps.executions.services import ExecutionService
        execution = ExecutionService.execute_workflow(
            workflow=workflow,
            input_data=input_data,
            triggered_by=request.user
        )

        from apps.executions.serializers import WorkflowExecutionSerializer
        return Response(
            WorkflowExecutionSerializer(execution).data,
            status=status.HTTP_201_CREATED
        )

    @action(detail=True, methods=['get'])
    def versions(self, request, pk=None):
        """Get all versions of a workflow."""
        workflow = self.get_object()
        versions = workflow.versions.all()

        serializer = WorkflowVersionSerializer(versions, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def create_version(self, request, pk=None):
        """Create a new version of the workflow."""
        workflow = self.get_object()
        serializer = CreateVersionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        definition = serializer.validated_data.get('definition', workflow.definition)
        change_summary = serializer.validated_data.get('change_summary')

        version = workflow.create_version(
            definition=definition,
            created_by=request.user
        )

        if change_summary:
            version.change_summary = change_summary
            version.save(update_fields=['change_summary'])

        return Response(
            WorkflowVersionSerializer(version).data,
            status=status.HTTP_201_CREATED
        )

    @action(detail=True, methods=['post'])
    def rollback(self, request, pk=None):
        """Rollback workflow to a specific version."""
        workflow = self.get_object()
        serializer = RollbackVersionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        version_number = serializer.validated_data['version_number']

        try:
            version = workflow.rollback_to_version(version_number)

            return Response({
                'message': f'Workflow rolled back to version {version_number}',
                'workflow': WorkflowSerializer(workflow).data,
                'version': WorkflowVersionSerializer(version).data
            })

        except WorkflowVersion.DoesNotExist:
            return Response(
                {'error': f'Version {version_number} not found'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['get'])
    def executions(self, request, pk=None):
        """Get all executions for this workflow."""
        workflow = self.get_object()
        from apps.executions.models import WorkflowExecution
        from apps.executions.serializers import WorkflowExecutionListSerializer

        executions = WorkflowExecution.objects.filter(
            workflow=workflow
        ).select_related('triggered_by').order_by('-created_at')

        # Pagination
        page = self.paginate_queryset(executions)
        if page is not None:
            serializer = WorkflowExecutionListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = WorkflowExecutionListSerializer(executions, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def statistics(self, request, pk=None):
        """Get workflow statistics."""
        workflow = self.get_object()
        stats = WorkflowService.get_workflow_statistics(workflow)
        return Response(stats)


class WorkflowVariableViewSet(viewsets.ModelViewSet):
    """
    ViewSet for WorkflowVariable model.

    list: Get all variables for a workflow
    create: Create a new variable
    retrieve: Get variable details
    update: Update variable
    partial_update: Partially update variable
    destroy: Delete variable
    """
    permission_classes = [IsAuthenticated, IsOrganizationMember]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']
    filterset_fields = ['variable_type', 'scope', 'is_required', 'is_secret']

    def get_queryset(self):
        """Get variables based on workflow context."""
        workflow_id = self.request.query_params.get('workflow')
        if not workflow_id:
            return WorkflowVariable.objects.none()

        return WorkflowVariable.objects.filter(workflow_id=workflow_id)

    def get_serializer_class(self):
        """Return serializer class."""
        return WorkflowVariableSerializer


class WorkflowTriggerViewSet(viewsets.ModelViewSet):
    """
    ViewSet for WorkflowTrigger model.

    list: Get all triggers for a workflow
    create: Create a new trigger
    retrieve: Get trigger details
    update: Update trigger
    partial_update: Partially update trigger
    destroy: Delete trigger
    """
    permission_classes = [IsAuthenticated, IsOrganizationMember]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['name', 'created_at', 'last_triggered_at']
    ordering = ['-created_at']
    filterset_fields = ['trigger_type', 'is_active']

    def get_queryset(self):
        """Get triggers based on workflow context."""
        workflow_id = self.request.query_params.get('workflow')
        if not workflow_id:
            return WorkflowTrigger.objects.none()

        return WorkflowTrigger.objects.filter(workflow_id=workflow_id)

    def get_serializer_class(self):
        """Return serializer class."""
        return WorkflowTriggerSerializer

    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """Activate a trigger."""
        trigger = self.get_object()
        trigger.is_active = True
        trigger.save(update_fields=['is_active', 'updated_at'])

        return Response({
            'message': 'Trigger activated successfully',
            'trigger': WorkflowTriggerSerializer(trigger).data
        })

    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """Deactivate a trigger."""
        trigger = self.get_object()
        trigger.is_active = False
        trigger.save(update_fields=['is_active', 'updated_at'])

        return Response({
            'message': 'Trigger deactivated successfully',
            'trigger': WorkflowTriggerSerializer(trigger).data
        })
