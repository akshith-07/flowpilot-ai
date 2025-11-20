"""
Celery configuration for FlowPilot AI.
"""
import os
from celery import Celery
from celery.schedules import crontab

# Set the default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')

app = Celery('flowpilot')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

# Celery Beat Schedule
app.conf.beat_schedule = {
    # Aggregate daily metrics (runs at midnight UTC)
    'aggregate-daily-metrics': {
        'task': 'apps.analytics.tasks.aggregate_daily_metrics',
        'schedule': crontab(hour=0, minute=0),
    },
    # Calculate monthly usage (runs on 1st of month at 1 AM UTC)
    'calculate-monthly-usage': {
        'task': 'apps.billing.tasks.calculate_monthly_usage',
        'schedule': crontab(hour=1, minute=0, day_of_month=1),
    },
    # Clean up expired sessions (daily at 2 AM UTC)
    'cleanup-expired-sessions': {
        'task': 'apps.users.tasks.cleanup_expired_sessions',
        'schedule': crontab(hour=2, minute=0),
    },
    # Refresh connector tokens (every 6 hours)
    'refresh-connector-tokens': {
        'task': 'apps.connectors.tasks.refresh_expiring_tokens',
        'schedule': crontab(minute=0, hour='*/6'),
    },
    # Clean up semantic cache (daily at 3 AM UTC)
    'cleanup-semantic-cache': {
        'task': 'apps.ai_engine.tasks.cleanup_expired_cache',
        'schedule': crontab(hour=3, minute=0),
    },
    # Check quota limits and send alerts (every hour)
    'check-quota-limits': {
        'task': 'apps.billing.tasks.check_quota_limits',
        'schedule': crontab(minute=0),
    },
}


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    """Debug task for testing Celery."""
    print(f'Request: {self.request!r}')
