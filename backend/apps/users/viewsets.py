"""
API viewsets for Users app.
"""
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenRefreshView
from django.contrib.auth import get_user_model
from .models import UserSession, MFADevice
from .serializers import (
    UserSerializer, UserRegistrationSerializer, LoginSerializer,
    PasswordChangeSerializer, PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer, UserSessionSerializer,
    MFADeviceSerializer, MFASetupSerializer, MFAVerifySerializer,
    MFADisableSerializer, OAuthConnectionSerializer
)
from .services import AuthenticationService, MFAService, SessionService
from core.exceptions import AuthenticationError, ValidationError
import logging

User = get_user_model()
logger = logging.getLogger(__name__)


class AuthViewSet(viewsets.GenericViewSet):
    """
    ViewSet for authentication endpoints.
    """
    permission_classes = [permissions.AllowAny]
    serializer_class = UserSerializer

    @action(detail=False, methods=['post'])
    def register(self, request):
        """
        Register a new user.

        POST /api/v1/auth/register/
        """
        serializer = UserRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = AuthenticationService.register_user(**serializer.validated_data)

        return Response({
            'success': True,
            'message': 'Registration successful. Please check your email to verify your account.',
            'data': {
                'user': UserSerializer(user).data
            }
        }, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'])
    def login(self, request):
        """
        Login user and return JWT tokens.

        POST /api/v1/auth/login/
        """
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            result = AuthenticationService.login_user(
                email=serializer.validated_data['email'],
                password=serializer.validated_data['password'],
                mfa_code=serializer.validated_data.get('mfa_code'),
                request=request
            )

            return Response({
                'success': True,
                'data': {
                    'user': UserSerializer(result['user']).data,
                    'access': result['access'],
                    'refresh': result['refresh']
                }
            })

        except AuthenticationError as e:
            if e.code == 'mfa_required':
                return Response({
                    'success': False,
                    'error': {
                        'code': 'mfa_required',
                        'message': str(e)
                    }
                }, status=status.HTTP_200_OK)  # Not an error, just needs MFA
            raise

    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def logout(self, request):
        """
        Logout user and invalidate refresh token.

        POST /api/v1/auth/logout/
        """
        refresh_token = request.data.get('refresh')
        if refresh_token:
            AuthenticationService.logout_user(request.user, refresh_token)

        return Response({
            'success': True,
            'message': 'Logout successful.'
        })

    @action(detail=False, methods=['post'])
    def verify_email(self, request):
        """
        Verify user email with token.

        POST /api/v1/auth/verify-email/
        """
        token = request.data.get('token')
        if not token:
            raise ValidationError('Verification token is required.')

        AuthenticationService.verify_email(token)

        return Response({
            'success': True,
            'message': 'Email verified successfully.'
        })

    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def change_password(self, request):
        """
        Change user password.

        POST /api/v1/auth/change-password/
        """
        serializer = PasswordChangeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        AuthenticationService.change_password(
            user=request.user,
            old_password=serializer.validated_data['old_password'],
            new_password=serializer.validated_data['new_password']
        )

        return Response({
            'success': True,
            'message': 'Password changed successfully. Please login again.'
        })

    @action(detail=False, methods=['post'])
    def reset_password_request(self, request):
        """
        Request password reset email.

        POST /api/v1/auth/reset-password-request/
        """
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Send password reset email (async task)
        from .tasks import send_password_reset_email
        send_password_reset_email.delay(serializer.validated_data['email'])

        return Response({
            'success': True,
            'message': 'Password reset instructions have been sent to your email.'
        })

    @action(detail=False, methods=['post'])
    def reset_password_confirm(self, request):
        """
        Confirm password reset with token.

        POST /api/v1/auth/reset-password-confirm/
        """
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # TODO: Implement password reset confirmation logic
        # This requires password reset token model or using JWT

        return Response({
            'success': True,
            'message': 'Password reset successful.'
        })


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for user management.
    """
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = User.objects.filter(is_active=True)

    @action(detail=False, methods=['get', 'patch'])
    def me(self, request):
        """
        Get or update current user profile.

        GET /api/v1/users/me/
        PATCH /api/v1/users/me/
        """
        if request.method == 'GET':
            serializer = self.get_serializer(request.user)
            return Response({
                'success': True,
                'data': serializer.data
            })

        elif request.method == 'PATCH':
            serializer = self.get_serializer(
                request.user,
                data=request.data,
                partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()

            return Response({
                'success': True,
                'data': serializer.data
            })


class SessionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for session management.
    """
    serializer_class = UserSessionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Get active sessions for current user."""
        return SessionService.get_active_sessions(self.request.user)

    @action(detail=False, methods=['get'])
    def active(self, request):
        """
        Get all active sessions.

        GET /api/v1/sessions/active/
        """
        sessions = self.get_queryset()
        serializer = self.get_serializer(sessions, many=True)

        return Response({
            'success': True,
            'count': sessions.count(),
            'data': serializer.data
        })

    @action(detail=True, methods=['post'])
    def revoke(self, request, pk=None):
        """
        Revoke a specific session.

        POST /api/v1/sessions/{id}/revoke/
        """
        SessionService.revoke_session(request.user, pk)

        return Response({
            'success': True,
            'message': 'Session revoked successfully.'
        })

    @action(detail=False, methods=['post'])
    def revoke_all(self, request):
        """
        Revoke all active sessions.

        POST /api/v1/sessions/revoke-all/
        """
        SessionService.revoke_all_sessions(request.user)

        return Response({
            'success': True,
            'message': 'All sessions revoked successfully.'
        })


class MFAViewSet(viewsets.GenericViewSet):
    """
    ViewSet for MFA management.
    """
    serializer_class = MFADeviceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Get MFA devices for current user."""
        return MFADevice.objects.filter(user=self.request.user, is_active=True)

    @action(detail=False, methods=['get'])
    def status(self, request):
        """
        Get MFA status for current user.

        GET /api/v1/mfa/status/
        """
        return Response({
            'success': True,
            'data': {
                'enabled': request.user.is_mfa_enabled,
                'devices': self.get_serializer(self.get_queryset(), many=True).data
            }
        })

    @action(detail=False, methods=['post'])
    def setup(self, request):
        """
        Setup MFA for current user.

        POST /api/v1/mfa/setup/
        """
        serializer = MFASetupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        device = MFAService.setup_mfa(
            user=request.user,
            device_name=serializer.validated_data.get('device_name', 'Authenticator App')
        )

        return Response({
            'success': True,
            'message': 'MFA setup initiated. Please scan the QR code with your authenticator app.',
            'data': MFADeviceSerializer(device).data
        })

    @action(detail=False, methods=['post'])
    def verify(self, request):
        """
        Verify MFA device with code.

        POST /api/v1/mfa/verify/
        """
        serializer = MFAVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        MFAService.verify_mfa(
            user=request.user,
            device_id=serializer.validated_data['device_id'],
            code=serializer.validated_data['code']
        )

        return Response({
            'success': True,
            'message': 'MFA verified successfully. Two-factor authentication is now enabled.'
        })

    @action(detail=False, methods=['post'])
    def disable(self, request):
        """
        Disable MFA for current user.

        POST /api/v1/mfa/disable/
        """
        serializer = MFADisableSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        MFAService.disable_mfa(
            user=request.user,
            password=serializer.validated_data['password']
        )

        return Response({
            'success': True,
            'message': 'MFA disabled successfully.'
        })
