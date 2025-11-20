"""
Business logic services for Executions app.
"""
from celery import shared_task
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


class ExecutionService:
    """Service class for execution-related business logic."""

    @staticmethod
    def execute_workflow(workflow, input_data=None, triggered_by=None, trigger=None):
        """
        Execute a workflow synchronously (creates execution and queues task).

        Args:
            workflow: Workflow instance
            input_data: Input data for execution
            triggered_by: User triggering the execution
            trigger: WorkflowTrigger instance

        Returns:
            WorkflowExecution: Created execution instance
        """
        from .models import WorkflowExecution

        if input_data is None:
            input_data = {}

        # Create execution
        execution = WorkflowExecution.objects.create(
            workflow=workflow,
            input_data=input_data,
            trigger=trigger,
            triggered_by=triggered_by,
            context={}
        )

        # Queue execution task
        ExecutionService.execute_workflow_async.delay(str(execution.id))

        return execution

    @staticmethod
    @shared_task(bind=True, max_retries=0)
    def execute_workflow_async(self, execution_id):
        """
        Execute workflow asynchronously (Celery task).

        Args:
            execution_id: UUID of the execution

        Returns:
            dict: Execution result
        """
        from .models import WorkflowExecution, ExecutionStep, ExecutionLog

        try:
            execution = WorkflowExecution.objects.get(id=execution_id)
            execution.start()

            # Get workflow definition
            definition = execution.workflow.definition
            nodes = definition.get('nodes', [])
            edges = definition.get('edges', [])

            # Initialize context with input data
            context = execution.input_data.copy()

            # Execute nodes in order (simplified - real implementation would handle graph traversal)
            step_number = 1

            for node in nodes:
                step = ExecutionStep.objects.create(
                    execution=execution,
                    node_id=node['id'],
                    node_type=node.get('type', 'unknown'),
                    node_name=node.get('name', node['id']),
                    step_number=step_number,
                    input_data=context
                )

                try:
                    step.start()

                    # Execute step based on type
                    output = ExecutionService._execute_node(node, context, execution, step)

                    # Update context with output
                    context[node['id']] = output

                    step.complete(output_data=output)

                    # Log success
                    ExecutionLog.objects.create(
                        execution=execution,
                        step=step,
                        level='info',
                        message=f'Step {step_number} completed successfully'
                    )

                except Exception as e:
                    error_message = str(e)
                    step.fail(error_message=error_message)

                    # Log error
                    ExecutionLog.objects.create(
                        execution=execution,
                        step=step,
                        level='error',
                        message=f'Step {step_number} failed: {error_message}'
                    )

                    # Fail entire execution
                    execution.fail(
                        error_message=f'Execution failed at step {step_number}: {error_message}'
                    )
                    return {
                        'execution_id': str(execution.id),
                        'status': 'failed',
                        'error': error_message
                    }

                step_number += 1

            # Complete execution
            execution.complete(output_data=context)

            return {
                'execution_id': str(execution.id),
                'status': 'completed',
                'output': context
            }

        except WorkflowExecution.DoesNotExist:
            logger.error(f'Execution {execution_id} not found')
            return {'status': 'error', 'message': 'Execution not found'}

        except Exception as e:
            logger.error(f'Error executing workflow: {str(e)}')
            if 'execution' in locals():
                execution.fail(error_message=str(e))
            return {'status': 'error', 'message': str(e)}

    @staticmethod
    def _execute_node(node, context, execution, step):
        """
        Execute a single node.

        Args:
            node: Node definition
            context: Execution context
            execution: WorkflowExecution instance
            step: ExecutionStep instance

        Returns:
            dict: Node output
        """
        node_type = node.get('type', 'unknown')

        # AI nodes
        if node_type.startswith('ai_'):
            from apps.ai_engine.services import AIService
            return AIService.execute_ai_node(node, context, execution, step)

        # Connector nodes
        elif node_type.startswith('connector_'):
            from apps.connectors.services import ConnectorService
            return ConnectorService.execute_connector_node(node, context, execution, step)

        # Action nodes
        elif node_type == 'email':
            return ExecutionService._execute_email_node(node, context)

        elif node_type == 'webhook':
            return ExecutionService._execute_webhook_node(node, context)

        elif node_type == 'delay':
            return ExecutionService._execute_delay_node(node, context)

        # Logic nodes
        elif node_type == 'condition':
            return ExecutionService._execute_condition_node(node, context)

        elif node_type == 'variable':
            return ExecutionService._execute_variable_node(node, context)

        else:
            return {'status': 'skipped', 'message': f'Unknown node type: {node_type}'}

    @staticmethod
    def _execute_email_node(node, context):
        """Execute email node."""
        # Simplified email execution
        return {'status': 'sent', 'message': 'Email sent successfully'}

    @staticmethod
    def _execute_webhook_node(node, context):
        """Execute webhook node."""
        # Simplified webhook execution
        return {'status': 'called', 'message': 'Webhook called successfully'}

    @staticmethod
    def _execute_delay_node(node, context):
        """Execute delay node."""
        import time
        delay_seconds = node.get('config', {}).get('seconds', 1)
        time.sleep(delay_seconds)
        return {'status': 'completed', 'delayed': delay_seconds}

    @staticmethod
    def _execute_condition_node(node, context):
        """Execute condition node."""
        condition = node.get('config', {}).get('condition', True)
        return {'status': 'evaluated', 'result': condition}

    @staticmethod
    def _execute_variable_node(node, context):
        """Execute variable node."""
        variable_name = node.get('config', {}).get('name')
        variable_value = node.get('config', {}).get('value')
        return {variable_name: variable_value}
