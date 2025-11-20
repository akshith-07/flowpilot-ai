"""
Celery tasks for Users app.
"""
from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone
from .models import UserSession
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def send_verification_email(self, user_id):
    """
    Send email verification email to user.

    Args:
        user_id: User ID
    """
    try:
        from .models import User
        user = User.objects.get(id=user_id)

        if user.email_verified:
            logger.info(f'Email already verified for user: {user.email}')
            return

        # Generate verification URL
        verification_url = f"{settings.FRONTEND_URL}/verify-email?token={user.email_verification_token}"

        # Send email
        subject = 'Verify Your Email - FlowPilot AI'
        message = f"""
        Hi {user.first_name},

        Welcome to FlowPilot AI! Please verify your email address by clicking the link below:

        {verification_url}

        This link will expire in 24 hours.

        If you didn't create an account, please ignore this email.

        Best regards,
        The FlowPilot AI Team
        """

        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )

        logger.info(f'Verification email sent to: {user.email}')

    except Exception as e:
        logger.error(f'Failed to send verification email: {str(e)}')
        raise self.retry(exc=e, countdown=60)


@shared_task(bind=True, max_retries=3)
def send_password_reset_email(self, email):
    """
    Send password reset email to user.

    Args:
        email: User email
    """
    try:
        from .models import User

        try:
            user = User.objects.get(email=email.lower())
        except User.DoesNotExist:
            # Don't reveal that user doesn't exist
            logger.info(f'Password reset requested for non-existent email: {email}')
            return

        # TODO: Generate password reset token (implement token model or use JWT)
        reset_token = "placeholder-token"
        reset_url = f"{settings.FRONTEND_URL}/reset-password?token={reset_token}"

        # Send email
        subject = 'Password Reset - FlowPilot AI'
        message = f"""
        Hi {user.first_name},

        You requested to reset your password. Click the link below to reset it:

        {reset_url}

        This link will expire in 1 hour.

        If you didn't request this, please ignore this email and your password will remain unchanged.

        Best regards,
        The FlowPilot AI Team
        """

        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )

        logger.info(f'Password reset email sent to: {user.email}')

    except Exception as e:
        logger.error(f'Failed to send password reset email: {str(e)}')
        raise self.retry(exc=e, countdown=60)


@shared_task
def cleanup_expired_sessions():
    """
    Clean up expired user sessions.
    Runs daily via Celery Beat.
    """
    try:
        cutoff_time = timezone.now()
        expired_sessions = UserSession.objects.filter(
            expires_at__lt=cutoff_time,
            is_active=True
        )

        count = expired_sessions.count()
        expired_sessions.update(is_active=False)

        logger.info(f'Cleaned up {count} expired sessions')

    except Exception as e:
        logger.error(f'Failed to cleanup expired sessions: {str(e)}')


@shared_task
def cleanup_old_login_attempts():
    """
    Clean up old login attempts (older than 30 days).
    Runs weekly via Celery Beat.
    """
    try:
        from .models import LoginAttempt
        cutoff_time = timezone.now() - timezone.timedelta(days=30)

        deleted_count, _ = LoginAttempt.objects.filter(
            attempted_at__lt=cutoff_time
        ).delete()

        logger.info(f'Cleaned up {deleted_count} old login attempts')

    except Exception as e:
        logger.error(f'Failed to cleanup old login attempts: {str(e)}')


@shared_task(bind=True, max_retries=3)
def send_welcome_email(self, user_id):
    """
    Send welcome email to new user after email verification.

    Args:
        user_id: User ID
    """
    try:
        from .models import User
        user = User.objects.get(id=user_id)

        subject = 'Welcome to FlowPilot AI!'
        message = f"""
        Hi {user.first_name},

        Welcome to FlowPilot AI! Your email has been verified successfully.

        You can now start building powerful AI-driven workflows to automate your business processes.

        Getting Started:
        - Create your first workflow
        - Connect your favorite tools
        - Explore our AI capabilities

        If you have any questions, feel free to reach out to our support team.

        Best regards,
        The FlowPilot AI Team
        """

        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )

        logger.info(f'Welcome email sent to: {user.email}')

    except Exception as e:
        logger.error(f'Failed to send welcome email: {str(e)}')
        raise self.retry(exc=e, countdown=60)
