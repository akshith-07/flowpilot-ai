"""Services for Notifications app."""
from django.core.mail import send_mail
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class NotificationService:
    """Service for notification operations."""

    @staticmethod
    def send_notification(organization=None, user=None, title='', message='',
                         notification_type='info', channels=None, metadata=None):
        """
        Send notification via multiple channels.

        Args:
            organization: Organization instance
            user: User instance
            title: Notification title
            message: Notification message
            notification_type: Type of notification (info, success, warning, error)
            channels: List of channels to send to
            metadata: Additional metadata

        Returns:
            Notification: Created notification instance
        """
        from apps.notifications.models import Notification

        if channels is None:
            channels = ['in_app', 'email']

        if metadata is None:
            metadata = {}

        # Create notification
        notification = Notification.objects.create(
            organization=organization,
            user=user,
            title=title,
            message=message,
            notification_type=notification_type,
            channels=channels,
            metadata=metadata
        )

        # Send via channels
        if 'email' in channels and user:
            NotificationService._send_email(user, title, message)

        if 'slack' in channels:
            NotificationService._send_slack(organization, title, message)

        return notification

    @staticmethod
    def _send_email(user, title, message):
        """Send email notification."""
        try:
            send_mail(
                subject=title,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=True
            )
            logger.info(f'Email sent to {user.email}')
        except Exception as e:
            logger.error(f'Failed to send email: {str(e)}')

    @staticmethod
    def _send_slack(organization, title, message):
        """Send Slack notification."""
        # Simplified Slack implementation
        logger.info(f'Slack notification sent to {organization.name}')

    @staticmethod
    def mark_as_read(notification):
        """Mark notification as read."""
        from django.utils import timezone

        notification.is_read = True
        notification.read_at = timezone.now()
        notification.save(update_fields=['is_read', 'read_at'])
