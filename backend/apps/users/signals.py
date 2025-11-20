"""
Django signals for Users app.
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=User)
def user_post_save(sender, instance, created, **kwargs):
    """
    Post-save signal for User model.
    Triggered after a user is created or updated.
    """
    if created:
        logger.info(f'New user created: {instance.email}')

        # Send welcome email after email verification
        # This will be triggered by email verification


@receiver(post_save, sender=User)
def user_email_verified(sender, instance, **kwargs):
    """
    Send welcome email when user email is verified.
    """
    if instance.email_verified and not kwargs.get('created', False):
        # Check if email was just verified (changed from False to True)
        try:
            old_instance = User.objects.get(pk=instance.pk)
            if hasattr(old_instance, 'email_verified') and not old_instance.email_verified:
                # Email was just verified
                from .tasks import send_welcome_email
                send_welcome_email.delay(instance.id)
        except User.DoesNotExist:
            pass
