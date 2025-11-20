"""
Celery tasks for Organizations app.
"""
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def send_invitation_email(self, invitation_id):
    """
    Send invitation email to user.

    Args:
        invitation_id: UUID of the invitation

    Returns:
        dict: Result with status
    """
    from .models import Invitation

    try:
        invitation = Invitation.objects.get(id=invitation_id)

        # Build invitation URL
        invitation_url = (
            f"{settings.FRONTEND_URL}/accept-invitation?"
            f"token={invitation.token}"
        )

        # Email content
        subject = f'Invitation to join {invitation.organization.name} on FlowPilot AI'
        message = f"""
        Hello,

        You have been invited to join {invitation.organization.name} on FlowPilot AI.

        Role: {invitation.role.name}
        Invited by: {invitation.invited_by.full_name if invitation.invited_by else 'System'}

        {f'Message: {invitation.message}' if invitation.message else ''}

        To accept this invitation, please click the link below:
        {invitation_url}

        This invitation will expire on {invitation.expires_at.strftime('%B %d, %Y at %I:%M %p')}.

        Best regards,
        FlowPilot AI Team
        """

        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[invitation.email],
            fail_silently=False,
        )

        logger.info(f'Invitation email sent to {invitation.email}')
        return {'status': 'success', 'email': invitation.email}

    except Invitation.DoesNotExist:
        logger.error(f'Invitation {invitation_id} not found')
        return {'status': 'error', 'message': 'Invitation not found'}

    except Exception as exc:
        logger.error(f'Error sending invitation email: {str(exc)}')
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))


@shared_task
def cleanup_expired_invitations():
    """
    Cleanup expired invitations.
    Mark pending invitations as expired if they have passed their expiry date.

    Returns:
        dict: Number of invitations marked as expired
    """
    from .models import Invitation

    expired_count = Invitation.objects.filter(
        status='pending',
        expires_at__lt=timezone.now()
    ).update(status='expired')

    logger.info(f'Marked {expired_count} invitations as expired')
    return {'expired_count': expired_count}


@shared_task
def reset_periodic_quotas():
    """
    Reset periodic usage quotas based on their period.
    Runs daily to check and reset quotas.

    Returns:
        dict: Number of quotas reset by period
    """
    from .models import UsageQuota

    now = timezone.now()
    reset_counts = {
        'daily': 0,
        'weekly': 0,
        'monthly': 0,
        'yearly': 0,
    }

    # Daily quotas
    daily_quotas = UsageQuota.objects.filter(
        period='daily',
        is_active=True,
        last_reset_at__lt=now - timedelta(days=1)
    )
    for quota in daily_quotas:
        quota.reset_usage()
        reset_counts['daily'] += 1

    # Weekly quotas
    weekly_quotas = UsageQuota.objects.filter(
        period='weekly',
        is_active=True,
        last_reset_at__lt=now - timedelta(weeks=1)
    )
    for quota in weekly_quotas:
        quota.reset_usage()
        reset_counts['weekly'] += 1

    # Monthly quotas
    monthly_quotas = UsageQuota.objects.filter(
        period='monthly',
        is_active=True,
        last_reset_at__lt=now - timedelta(days=30)
    )
    for quota in monthly_quotas:
        quota.reset_usage()
        reset_counts['monthly'] += 1

    # Yearly quotas
    yearly_quotas = UsageQuota.objects.filter(
        period='yearly',
        is_active=True,
        last_reset_at__lt=now - timedelta(days=365)
    )
    for quota in yearly_quotas:
        quota.reset_usage()
        reset_counts['yearly'] += 1

    logger.info(f'Reset quotas: {reset_counts}')
    return reset_counts


@shared_task
def send_quota_alerts():
    """
    Send alerts for quotas approaching or exceeding limits.

    Returns:
        dict: Number of alerts sent
    """
    from .models import UsageQuota
    from apps.notifications.services import NotificationService

    warning_alerts = 0
    critical_alerts = 0

    # Get quotas approaching warning threshold
    warning_quotas = UsageQuota.objects.filter(
        is_active=True,
        is_alert_threshold_reached=False
    ).exclude(
        is_warning_threshold_reached=False
    )

    for quota in warning_quotas:
        # Send warning notification
        NotificationService.send_notification(
            organization=quota.organization,
            title=f'{quota.quota_type} quota warning',
            message=(
                f'Your {quota.quota_type} usage is at '
                f'{quota.usage_percentage:.1f}% '
                f'({quota.current_usage}/{quota.limit})'
            ),
            notification_type='warning',
            metadata={'quota_id': str(quota.id)}
        )
        warning_alerts += 1

    # Get quotas approaching alert threshold
    alert_quotas = UsageQuota.objects.filter(
        is_active=True,
        is_alert_threshold_reached=True
    )

    for quota in alert_quotas:
        # Send critical notification
        NotificationService.send_notification(
            organization=quota.organization,
            title=f'{quota.quota_type} quota critical',
            message=(
                f'Your {quota.quota_type} usage is at '
                f'{quota.usage_percentage:.1f}% '
                f'({quota.current_usage}/{quota.limit}). '
                'Please upgrade your plan or contact support.'
            ),
            notification_type='error',
            metadata={'quota_id': str(quota.id)}
        )
        critical_alerts += 1

    logger.info(
        f'Sent {warning_alerts} warning alerts and '
        f'{critical_alerts} critical alerts'
    )

    return {
        'warning_alerts': warning_alerts,
        'critical_alerts': critical_alerts
    }


@shared_task(bind=True, max_retries=3)
def send_member_added_notification(self, member_id):
    """
    Send notification when a member is added to organization.

    Args:
        member_id: UUID of the organization member

    Returns:
        dict: Result with status
    """
    from .models import OrganizationMember
    from apps.notifications.services import NotificationService

    try:
        member = OrganizationMember.objects.get(id=member_id)

        # Send notification to organization admins
        NotificationService.send_notification(
            organization=member.organization,
            title='New member added',
            message=(
                f'{member.user.full_name} ({member.user.email}) '
                f'has been added to {member.organization.name} '
                f'with role {member.role.name}'
            ),
            notification_type='info',
            metadata={'member_id': str(member.id)}
        )

        logger.info(f'Member added notification sent for {member.user.email}')
        return {'status': 'success'}

    except OrganizationMember.DoesNotExist:
        logger.error(f'Member {member_id} not found')
        return {'status': 'error', 'message': 'Member not found'}

    except Exception as exc:
        logger.error(f'Error sending member added notification: {str(exc)}')
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))


@shared_task
def generate_organization_report(organization_id, report_type='monthly'):
    """
    Generate organization usage report.

    Args:
        organization_id: UUID of the organization
        report_type: Type of report (daily, weekly, monthly)

    Returns:
        dict: Report data
    """
    from .models import Organization
    from .services import OrganizationService

    try:
        organization = Organization.objects.get(id=organization_id)
        stats = OrganizationService.get_organization_statistics(organization)

        # Add report metadata
        report = {
            'organization': {
                'id': str(organization.id),
                'name': organization.name,
            },
            'report_type': report_type,
            'generated_at': timezone.now().isoformat(),
            'statistics': stats,
        }

        logger.info(f'Generated {report_type} report for {organization.name}')
        return report

    except Organization.DoesNotExist:
        logger.error(f'Organization {organization_id} not found')
        return {'status': 'error', 'message': 'Organization not found'}
