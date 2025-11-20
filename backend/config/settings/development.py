"""Development settings."""
from .base import *

# Debug mode
DEBUG = True

# Allowed hosts
ALLOWED_HOSTS = ['*']

# CORS for development
CORS_ALLOW_ALL_ORIGINS = True

# Additional apps for development
INSTALLED_APPS += [
    'django_extensions',
    'debug_toolbar',
]

# Debug Toolbar Middleware
MIDDLEWARE += [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

# Internal IPs for Debug Toolbar
INTERNAL_IPS = [
    '127.0.0.1',
    'localhost',
]

# Disable template caching
TEMPLATES[0]['OPTIONS']['debug'] = True

# Email backend for development
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Celery eager mode for development (synchronous execution)
CELERY_TASK_ALWAYS_EAGER = env.bool('CELERY_TASK_ALWAYS_EAGER', default=False)
CELERY_TASK_EAGER_PROPAGATES = True

# Additional logging for development
LOGGING['loggers']['django.db.backends'] = {
    'handlers': ['console'],
    'level': 'DEBUG',
    'propagate': False,
}
