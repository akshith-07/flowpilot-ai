"""
Business logic services for Users app.
"""
from django.contrib.auth import authenticate
from django.utils import timezone
from django.conf import settings
from django.db import transaction
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User, UserSession, LoginAttempt, MFADevice
from core.exceptions import (
    AuthenticationError, ValidationError, NotFoundError
)
from core.utils import generate_random_string, hash_string, get_client_ip, get_user_agent
import logging
import pyotp

logger = logging.getLogger(__name__)


class AuthenticationService:
    """Service for user authentication operations."""

    @staticmethod
    def register_user(email, password, first_name, last_name, **kwargs):
        """
        Register a new user.

        Args:
            email: User email
            password: User password
            first_name: First name
            last_name: Last name
            **kwargs: Additional user fields

        Returns:
            User: Created user instance

        Raises:
            ValidationError: If validation fails
        """
        try:
            with transaction.atomic():
                user = User.objects.create_user(
                    email=email.lower(),
                    password=password,
                    first_name=first_name,
                    last_name=last_name,
                    **kwargs
                )

                # Generate email verification token
                user.email_verification_token = generate_random_string(32)
                user.save(update_fields=['email_verification_token'])

                # Send verification email (async task)
                from .tasks import send_verification_email
                send_verification_email.delay(user.id)

                logger.info(f'User registered: {user.email}')
                return user

        except Exception as e:
            logger.error(f'User registration failed: {str(e)}')
            raise ValidationError(f'Registration failed: {str(e)}')

    @staticmethod
    def login_user(email, password, mfa_code=None, request=None):
        """
        Authenticate user and create session.

        Args:
            email: User email
            password: User password
            mfa_code: MFA code (if MFA is enabled)
            request: HTTP request object

        Returns:
            dict: Token response with access and refresh tokens

        Raises:
            AuthenticationError: If authentication fails
        """
        ip_address = get_client_ip(request) if request else None
        user_agent = get_user_agent(request) if request else None

        # Check if account is locked
        if LoginAttempt.is_account_locked(email):
            AuthenticationService._log_login_attempt(
                email, ip_address, user_agent, False, 'account_locked'
            )
            raise AuthenticationError(
                'Account is locked due to too many failed login attempts. '
                f'Please try again in {settings.ACCOUNT_LOCKOUT_DURATION} minutes.'
            )

        # Authenticate user
        user = authenticate(username=email, password=password)
        if not user:
            AuthenticationService._log_login_attempt(
                email, ip_address, user_agent, False, 'invalid_credentials'
            )
            raise AuthenticationError('Invalid email or password.')

        # Check if account is active
        if not user.is_active:
            AuthenticationService._log_login_attempt(
                email, ip_address, user_agent, False, 'account_inactive'
            )
            raise AuthenticationError('Account is inactive.')

        # Check MFA if enabled
        if user.is_mfa_enabled:
            if not mfa_code:
                raise AuthenticationError('MFA code is required.', code='mfa_required')

            if not AuthenticationService._verify_mfa(user, mfa_code):
                AuthenticationService._log_login_attempt(
                    email, ip_address, user_agent, False, 'mfa_failed'
                )
                raise AuthenticationError('Invalid MFA code.')

        # Create session
        tokens = AuthenticationService._create_session(user, request)

        # Log successful login
        AuthenticationService._log_login_attempt(
            email, ip_address, user_agent, True, None
        )

        # Update last login
        user.last_login = timezone.now()
        user.save(update_fields=['last_login'])

        logger.info(f'User logged in: {user.email}')

        return {
            'user': user,
            'access': tokens['access'],
            'refresh': tokens['refresh']
        }

    @staticmethod
    def _verify_mfa(user, code):
        """Verify MFA code."""
        mfa_device = user.mfa_devices.filter(
            is_active=True,
            is_verified=True,
            device_type='totp'
        ).first()

        if not mfa_device:
            return False

        if mfa_device.verify_token(code):
            mfa_device.last_used_at = timezone.now()
            mfa_device.save(update_fields=['last_used_at'])
            return True

        return False

    @staticmethod
    def _create_session(user, request):
        """Create user session and generate tokens."""
        refresh = RefreshToken.for_user(user)

        # Create session record
        session = UserSession.objects.create(
            user=user,
            refresh_token_hash=hash_string(str(refresh)),
            ip_address=get_client_ip(request) if request else None,
            user_agent=get_user_agent(request) if request else None,
            expires_at=timezone.now() + settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME']
        )

        # Parse user agent for device info (simplified)
        if request:
            user_agent_str = get_user_agent(request)
            session.device_name = user_agent_str[:100] if user_agent_str else 'Unknown'
            session.device_type = 'web'
            session.save(update_fields=['device_name', 'device_type'])

        return {
            'access': str(refresh.access_token),
            'refresh': str(refresh)
        }

    @staticmethod
    def _log_login_attempt(email, ip_address, user_agent, success, failure_reason):
        """Log login attempt."""
        LoginAttempt.objects.create(
            email=email,
            ip_address=ip_address,
            user_agent=user_agent,
            success=success,
            failure_reason=failure_reason
        )

    @staticmethod
    def logout_user(user, refresh_token):
        """
        Logout user and invalidate session.

        Args:
            user: User instance
            refresh_token: Refresh token to invalidate
        """
        try:
            # Invalidate session
            token_hash = hash_string(refresh_token)
            UserSession.objects.filter(
                user=user,
                refresh_token_hash=token_hash,
                is_active=True
            ).update(is_active=False)

            # Blacklist token
            refresh = RefreshToken(refresh_token)
            refresh.blacklist()

            logger.info(f'User logged out: {user.email}')

        except Exception as e:
            logger.error(f'Logout failed: {str(e)}')

    @staticmethod
    def change_password(user, old_password, new_password):
        """
        Change user password.

        Args:
            user: User instance
            old_password: Current password
            new_password: New password

        Raises:
            AuthenticationError: If old password is incorrect
        """
        if not user.check_password(old_password):
            raise AuthenticationError('Current password is incorrect.')

        user.set_password(new_password)
        user.password_changed_at = timezone.now()
        user.save(update_fields=['password', 'password_changed_at'])

        # Invalidate all sessions except current
        UserSession.objects.filter(user=user, is_active=True).update(is_active=False)

        logger.info(f'Password changed for user: {user.email}')

    @staticmethod
    def verify_email(token):
        """
        Verify user email with token.

        Args:
            token: Verification token

        Raises:
            ValidationError: If token is invalid
        """
        try:
            user = User.objects.get(email_verification_token=token)
            user.email_verified = True
            user.email_verification_token = None
            user.save(update_fields=['email_verified', 'email_verification_token'])

            logger.info(f'Email verified for user: {user.email}')

        except User.DoesNotExist:
            raise ValidationError('Invalid or expired verification token.')


class MFAService:
    """Service for MFA operations."""

    @staticmethod
    def setup_mfa(user, device_name='Authenticator App'):
        """
        Setup MFA for user.

        Args:
            user: User instance
            device_name: Name for the device

        Returns:
            MFADevice: Created MFA device
        """
        # Check if user already has an active TOTP device
        existing = user.mfa_devices.filter(
            device_type='totp',
            is_active=True
        ).first()

        if existing and existing.is_verified:
            raise ValidationError('MFA is already enabled for this account.')

        # Delete any unverified devices
        user.mfa_devices.filter(
            device_type='totp',
            is_verified=False
        ).delete()

        # Create new device
        secret = MFADevice.generate_secret()
        device = MFADevice.objects.create(
            user=user,
            device_name=device_name,
            device_type='totp',
            secret_encrypted=secret,
            is_active=True,
            is_verified=False
        )

        logger.info(f'MFA setup initiated for user: {user.email}')

        return device

    @staticmethod
    def verify_mfa(user, device_id, code):
        """
        Verify MFA device with code.

        Args:
            user: User instance
            device_id: MFA device ID
            code: TOTP code

        Raises:
            ValidationError: If verification fails
        """
        try:
            device = user.mfa_devices.get(id=device_id, is_active=True)
        except MFADevice.DoesNotExist:
            raise NotFoundError('MFA device not found.')

        if device.is_verified:
            raise ValidationError('MFA device is already verified.')

        if not device.verify_token(code):
            raise ValidationError('Invalid MFA code.')

        device.is_verified = True
        device.verified_at = timezone.now()
        device.save(update_fields=['is_verified', 'verified_at'])

        logger.info(f'MFA verified for user: {user.email}')

    @staticmethod
    def disable_mfa(user, password):
        """
        Disable MFA for user.

        Args:
            user: User instance
            password: User password for confirmation

        Raises:
            AuthenticationError: If password is incorrect
        """
        if not user.check_password(password):
            raise AuthenticationError('Password is incorrect.')

        user.mfa_devices.filter(is_active=True).update(is_active=False)

        logger.info(f'MFA disabled for user: {user.email}')


class SessionService:
    """Service for session management."""

    @staticmethod
    def get_active_sessions(user):
        """
        Get all active sessions for user.

        Args:
            user: User instance

        Returns:
            QuerySet: Active sessions
        """
        return UserSession.objects.filter(
            user=user,
            is_active=True,
            expires_at__gt=timezone.now()
        ).order_by('-last_activity')

    @staticmethod
    def revoke_session(user, session_id):
        """
        Revoke a specific session.

        Args:
            user: User instance
            session_id: Session ID to revoke

        Raises:
            NotFoundError: If session not found
        """
        try:
            session = UserSession.objects.get(
                id=session_id,
                user=user,
                is_active=True
            )
            session.is_active = False
            session.save(update_fields=['is_active'])

            logger.info(f'Session revoked for user: {user.email}')

        except UserSession.DoesNotExist:
            raise NotFoundError('Session not found.')

    @staticmethod
    def revoke_all_sessions(user):
        """
        Revoke all active sessions for user.

        Args:
            user: User instance
        """
        UserSession.objects.filter(
            user=user,
            is_active=True
        ).update(is_active=False)

        logger.info(f'All sessions revoked for user: {user.email}')
