"""
Custom exception classes and exception handler for FlowPilot AI.
"""
from rest_framework import status
from rest_framework.views import exception_handler as drf_exception_handler
from rest_framework.response import Response
import logging

logger = logging.getLogger(__name__)


class FlowPilotException(Exception):
    """Base exception for FlowPilot AI."""
    default_message = 'An error occurred'
    default_code = 'error'
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

    def __init__(self, message=None, code=None, status_code=None):
        self.message = message or self.default_message
        self.code = code or self.default_code
        if status_code:
            self.status_code = status_code
        super().__init__(self.message)


class ValidationError(FlowPilotException):
    """Validation error."""
    default_message = 'Validation failed'
    default_code = 'validation_error'
    status_code = status.HTTP_400_BAD_REQUEST


class AuthenticationError(FlowPilotException):
    """Authentication error."""
    default_message = 'Authentication failed'
    default_code = 'authentication_error'
    status_code = status.HTTP_401_UNAUTHORIZED


class PermissionDeniedError(FlowPilotException):
    """Permission denied error."""
    default_message = 'Permission denied'
    default_code = 'permission_denied'
    status_code = status.HTTP_403_FORBIDDEN


class NotFoundError(FlowPilotException):
    """Resource not found error."""
    default_message = 'Resource not found'
    default_code = 'not_found'
    status_code = status.HTTP_404_NOT_FOUND


class QuotaExceededError(FlowPilotException):
    """Quota exceeded error."""
    default_message = 'Quota exceeded'
    default_code = 'quota_exceeded'
    status_code = status.HTTP_429_TOO_MANY_REQUESTS


class WorkflowExecutionError(FlowPilotException):
    """Workflow execution error."""
    default_message = 'Workflow execution failed'
    default_code = 'execution_error'
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR


class AIServiceError(FlowPilotException):
    """AI service error."""
    default_message = 'AI service error'
    default_code = 'ai_service_error'
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR


class ConnectorError(FlowPilotException):
    """Connector error."""
    default_message = 'Connector error'
    default_code = 'connector_error'
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR


class DocumentProcessingError(FlowPilotException):
    """Document processing error."""
    default_message = 'Document processing failed'
    default_code = 'document_processing_error'
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR


def custom_exception_handler(exc, context):
    """
    Custom exception handler that handles FlowPilot exceptions
    and formats all errors consistently.

    Args:
        exc: The exception raised
        context: The context in which the exception occurred

    Returns:
        Response: Formatted error response
    """
    # Call DRF's default exception handler first
    response = drf_exception_handler(exc, context)

    if response is not None:
        # DRF handled the exception
        error_data = {
            'success': False,
            'error': {
                'code': getattr(exc, 'default_code', 'error'),
                'message': str(exc),
                'details': response.data
            }
        }
        response.data = error_data
        return response

    # Handle FlowPilot custom exceptions
    if isinstance(exc, FlowPilotException):
        logger.error(f'{exc.code}: {exc.message}', exc_info=True)
        return Response(
            {
                'success': False,
                'error': {
                    'code': exc.code,
                    'message': exc.message,
                }
            },
            status=exc.status_code
        )

    # Handle unexpected exceptions
    logger.exception('Unhandled exception occurred', exc_info=True)
    return Response(
        {
            'success': False,
            'error': {
                'code': 'internal_server_error',
                'message': 'An unexpected error occurred',
            }
        },
        status=status.HTTP_500_INTERNAL_SERVER_ERROR
    )
