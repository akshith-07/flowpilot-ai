"""
SSO signals for event handling.
"""
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver

from .models import SSOConnection, SSOSession


@receiver(post_save, sender=SSOConnection)
def log_connection_update(sender, instance, created, **kwargs):
    """Log SSO connection creation/update."""
    from .models import SSOAuditLog

    if created:
        SSOAuditLog.log_event(
            event_type='connection_created',
            message=f'SSO connection created: {instance.name}',
            connection=instance,
            organization=instance.organization,
            user=instance.created_by,
            severity='info'
        )


@receiver(pre_delete, sender=SSOSession)
def log_session_deletion(sender, instance, **kwargs):
    """Log SSO session deletion."""
    from .models import SSOAuditLog

    if instance.is_active:
        SSOAuditLog.log_event(
            event_type='logout',
            message='SSO session deleted',
            user=instance.user,
            connection=instance.connection,
            session=instance,
            organization=instance.connection.organization,
            email=instance.user.email,
            provider_name=instance.connection.provider.display_name,
            severity='info'
        )
