"""
Celery tasks for Notifications app.
"""
from celery import shared_task
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def send_notification(self, notification_id):
    """
    Send notification via configured channels.

    Args:
        notification_id: Notification ID
    """
    try:
        from .models import Notification
        from .services import NotificationService
        from django.utils import timezone

        notification = Notification.objects.get(id=notification_id)

        # Send via appropriate channel
        result = NotificationService.send(notification)

        # Update notification
        if result.get('success'):
            notification.sent_at = timezone.now()
            notification.metadata['sent_result'] = result
            notification.save(update_fields=['sent_at', 'metadata'])

        logger.info(f'Notification sent: {notification_id}')

    except Exception as e:
        logger.error(f'Failed to send notification: {str(e)}')
        raise self.retry(exc=e, countdown=60)


@shared_task(bind=True)
def process_alert_rules(self):
    """
    Process and trigger alert rules.
    """
    try:
        from .models import AlertRule
        from .services import NotificationService

        # Get all active alert rules
        alert_rules = AlertRule.objects.filter(is_active=True)

        for rule in alert_rules:
            try:
                # Check if rule conditions are met
                if NotificationService.evaluate_alert_rule(rule):
                    # Trigger actions
                    NotificationService.trigger_alert_actions(rule)

                    logger.info(f'Alert rule triggered: {rule.id}')
            except Exception as e:
                logger.error(f'Failed to process alert rule {rule.id}: {str(e)}')

    except Exception as e:
        logger.error(f'Failed to process alert rules: {str(e)}')
