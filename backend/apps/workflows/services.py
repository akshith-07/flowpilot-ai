"""
Business logic services for Workflows app.
"""
from django.db.models import Count, Avg, Q, F
from django.utils import timezone
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)


class WorkflowService:
    """Service class for workflow-related business logic."""

    @staticmethod
    def test_workflow(workflow, input_data=None, dry_run=True):
        """
        Test workflow execution with mock data.

        Args:
            workflow: Workflow instance
            input_data: Input data for testing
            dry_run: Whether to perform a dry run

        Returns:
            dict: Test results
        """
        if input_data is None:
            input_data = {}

        # Validate workflow definition
        validation_errors = WorkflowService.validate_workflow_definition(
            workflow.definition
        )

        if validation_errors:
            return {
                'valid': False,
                'errors': validation_errors,
                'warnings': []
            }

        # Simulate execution
        warnings = []

        # Check for required variables
        for variable in workflow.variables.filter(is_required=True):
            if variable.name not in input_data:
                warnings.append(
                    f'Required variable "{variable.name}" not provided in input data'
                )

        return {
            'valid': True,
            'errors': [],
            'warnings': warnings,
            'input_data': input_data,
            'dry_run': dry_run,
            'node_count': len(workflow.definition.get('nodes', [])),
            'edge_count': len(workflow.definition.get('edges', [])),
        }

    @staticmethod
    def validate_workflow_definition(definition):
        """
        Validate workflow definition structure.

        Args:
            definition: Workflow definition dict

        Returns:
            list: Validation errors
        """
        errors = []

        if not isinstance(definition, dict):
            errors.append('Definition must be a JSON object')
            return errors

        # Check required keys
        if 'nodes' not in definition:
            errors.append('Definition must contain "nodes" key')

        if 'edges' not in definition:
            errors.append('Definition must contain "edges" key')

        if errors:
            return errors

        # Validate nodes
        nodes = definition.get('nodes', [])
        node_ids = set()

        for i, node in enumerate(nodes):
            if not isinstance(node, dict):
                errors.append(f'Node at index {i} is not an object')
                continue

            if 'id' not in node:
                errors.append(f'Node at index {i} missing "id" field')
            else:
                node_id = node['id']
                if node_id in node_ids:
                    errors.append(f'Duplicate node ID: {node_id}')
                node_ids.add(node_id)

            if 'type' not in node:
                errors.append(f'Node at index {i} missing "type" field')

        # Validate edges
        edges = definition.get('edges', [])

        for i, edge in enumerate(edges):
            if not isinstance(edge, dict):
                errors.append(f'Edge at index {i} is not an object')
                continue

            if 'source' not in edge:
                errors.append(f'Edge at index {i} missing "source" field')
            elif edge['source'] not in node_ids:
                errors.append(
                    f'Edge at index {i} has invalid source: {edge["source"]}'
                )

            if 'target' not in edge:
                errors.append(f'Edge at index {i} missing "target" field')
            elif edge['target'] not in node_ids:
                errors.append(
                    f'Edge at index {i} has invalid target: {edge["target"]}'
                )

        return errors

    @staticmethod
    def get_workflow_statistics(workflow):
        """
        Get comprehensive statistics for a workflow.

        Args:
            workflow: Workflow instance

        Returns:
            dict: Statistics
        """
        from apps.executions.models import WorkflowExecution

        executions = WorkflowExecution.objects.filter(workflow=workflow)

        # Overall stats
        total_executions = executions.count()
        successful = executions.filter(status='completed').count()
        failed = executions.filter(status='failed').count()
        running = executions.filter(status='running').count()

        # Time-based stats
        last_30_days = timezone.now() - timedelta(days=30)
        recent_executions = executions.filter(created_at__gte=last_30_days)

        # Average duration
        completed_executions = executions.filter(
            status='completed',
            duration__isnull=False
        )

        avg_duration = completed_executions.aggregate(
            avg=Avg('duration')
        )['avg'] or 0

        stats = {
            'total_executions': total_executions,
            'successful_executions': successful,
            'failed_executions': failed,
            'running_executions': running,
            'success_rate': workflow.success_rate,
            'average_duration_seconds': avg_duration,
            'last_30_days': {
                'total': recent_executions.count(),
                'successful': recent_executions.filter(status='completed').count(),
                'failed': recent_executions.filter(status='failed').count(),
            },
            'triggers': {
                'total': workflow.triggers.count(),
                'active': workflow.triggers.filter(is_active=True).count(),
                'by_type': dict(
                    workflow.triggers.values('trigger_type')
                    .annotate(count=Count('id'))
                    .values_list('trigger_type', 'count')
                ),
            },
            'variables': {
                'total': workflow.variables.count(),
                'required': workflow.variables.filter(is_required=True).count(),
                'secret': workflow.variables.filter(is_secret=True).count(),
            },
            'versions': {
                'total': workflow.versions.count(),
                'current': workflow.version,
            },
        }

        return stats

    @staticmethod
    def get_popular_templates(limit=10):
        """
        Get most popular workflow templates.

        Args:
            limit: Number of templates to return

        Returns:
            QuerySet: Popular templates
        """
        from .models import WorkflowTemplate

        return WorkflowTemplate.objects.filter(
            is_public=True
        ).order_by('-use_count')[:limit]

    @staticmethod
    def search_workflows(organization, query):
        """
        Search workflows by name, description, or tags.

        Args:
            organization: Organization instance
            query: Search query

        Returns:
            QuerySet: Matching workflows
        """
        from .models import Workflow

        return Workflow.objects.filter(
            organization=organization
        ).filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(tags__contains=[query])
        )

    @staticmethod
    def get_workflow_dependencies(workflow):
        """
        Get workflow dependencies (connectors, variables, etc.).

        Args:
            workflow: Workflow instance

        Returns:
            dict: Dependencies
        """
        definition = workflow.definition
        nodes = definition.get('nodes', [])

        # Extract connector nodes
        connector_nodes = [
            node for node in nodes
            if node.get('type', '').startswith('connector_')
        ]

        # Extract AI nodes
        ai_nodes = [
            node for node in nodes
            if node.get('type', '').startswith('ai_')
        ]

        # Extract action nodes
        action_nodes = [
            node for node in nodes
            if node.get('type', '') in ['email', 'webhook', 'http_request']
        ]

        dependencies = {
            'connectors': len(connector_nodes),
            'ai_nodes': len(ai_nodes),
            'action_nodes': len(action_nodes),
            'total_nodes': len(nodes),
            'variables': workflow.variables.count(),
            'triggers': workflow.triggers.filter(is_active=True).count(),
        }

        return dependencies
