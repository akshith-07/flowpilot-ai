"""
Core views for health checks and system monitoring.
"""
from django.http import JsonResponse
from django.db import connection
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)


def health_check(request):
    """
    Basic health check endpoint.
    Returns 200 if the service is running.
    """
    return JsonResponse({
        'status': 'healthy',
        'service': 'FlowPilot AI',
        'version': '1.0.0'
    })


def database_check(request):
    """
    Database health check.
    Verifies database connectivity.
    """
    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT 1')
        return JsonResponse({
            'status': 'healthy',
            'database': 'connected'
        })
    except Exception as e:
        logger.error(f'Database health check failed: {str(e)}')
        return JsonResponse({
            'status': 'unhealthy',
            'database': 'disconnected',
            'error': str(e)
        }, status=503)


def cache_check(request):
    """
    Cache health check.
    Verifies Redis connectivity.
    """
    try:
        cache.set('health_check', 'ok', 10)
        value = cache.get('health_check')
        if value == 'ok':
            return JsonResponse({
                'status': 'healthy',
                'cache': 'connected'
            })
        else:
            raise Exception('Cache value mismatch')
    except Exception as e:
        logger.error(f'Cache health check failed: {str(e)}')
        return JsonResponse({
            'status': 'unhealthy',
            'cache': 'disconnected',
            'error': str(e)
        }, status=503)
