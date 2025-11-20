"""
SSO views and viewsets for API endpoints.
"""
from django.shortcuts import redirect
from django.db.models import Q, Count
from django.utils import timezone
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError, PermissionDenied
from rest_framework_simplejwt.tokens import RefreshToken

from apps.core.permissions import IsOrganizationMember, IsOrganizationAdmin
from .models import (
    SSOProvider, SSOConnection, SSOSession,
    SSOAuditLog, SSOStateToken
)
from .serializers import (
    SSOProviderSerializer, SSOProviderListSerializer,
    SSOConnectionSerializer, SSOConnectionCreateSerializer,
    SSOConnectionUpdateSerializer, SSOSessionSerializer,
    SSOAuditLogSerializer, SSOInitiateLoginSerializer,
    SSOCallbackSerializer, SSOTestConnectionSerializer,
    SAMLMetadataSerializer, SSOConnectionStatsSerializer
)
from .services import (
    OAuth2Service, OIDCService, SAMLService,
    UserProvisioningService, SSOSessionService
)


class SSOProviderViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for SSO providers.
    Read-only - providers are managed by administrators.
    """
    queryset = SSOProvider.objects.filter(is_enabled=True)
    serializer_class = SSOProviderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'list':
            return SSOProviderListSerializer
        return SSOProviderSerializer

    @action(detail=False, methods=['get'])
    def available(self, request):
        """
        Get available SSO providers for current organization.
        """
        organization_id = request.query_params.get('organization_id')
        if not organization_id:
            return Response(
                {'error': 'organization_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get all available providers
        providers = self.get_queryset()

        # Get configured connections for organization
        configured_providers = SSOConnection.objects.filter(
            organization_id=organization_id
        ).values_list('provider_id', flat=True)

        serializer = self.get_serializer(providers, many=True)
        data = serializer.data

        # Mark configured providers
        for item in data:
            item['is_configured'] = str(item['id']) in map(str, configured_providers)

        return Response(data)


class SSOConnectionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for SSO connections.
    Manages organization-specific SSO configurations.
    """
    queryset = SSOConnection.objects.all()
    serializer_class = SSOConnectionSerializer
    permission_classes = [permissions.IsAuthenticated, IsOrganizationMember]

    def get_queryset(self):
        """Filter connections by organization."""
        queryset = super().get_queryset()

        # Filter by organization if provided
        organization_id = self.request.query_params.get('organization_id')
        if organization_id:
            queryset = queryset.filter(organization_id=organization_id)

        # Filter by provider if provided
        provider_id = self.request.query_params.get('provider_id')
        if provider_id:
            queryset = queryset.filter(provider_id=provider_id)

        # Filter by status if provided
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        return queryset.select_related('provider', 'organization')

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'create':
            return SSOConnectionCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return SSOConnectionUpdateSerializer
        return SSOConnectionSerializer

    def perform_create(self, serializer):
        """Create SSO connection."""
        # Check if user is admin of organization
        organization = serializer.validated_data.get('organization')
        if not self.request.user.is_superuser:
            if not organization.members.filter(
                user=self.request.user,
                role__name__in=['Owner', 'Admin']
            ).exists():
                raise PermissionDenied('Only organization admins can create SSO connections')

        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        """Update SSO connection."""
        # Check if user is admin of organization
        connection = self.get_object()
        if not self.request.user.is_superuser:
            if not connection.organization.members.filter(
                user=self.request.user,
                role__name__in=['Owner', 'Admin']
            ).exists():
                raise PermissionDenied('Only organization admins can update SSO connections')

        serializer.save()

    def perform_destroy(self, instance):
        """Delete SSO connection."""
        # Check if user is admin of organization
        if not self.request.user.is_superuser:
            if not instance.organization.members.filter(
                user=self.request.user,
                role__name__in=['Owner', 'Admin']
            ).exists():
                raise PermissionDenied('Only organization admins can delete SSO connections')

        # Deactivate all sessions
        SSOSession.objects.filter(connection=instance, is_active=True).update(
            is_active=False
        )

        # Log deletion
        SSOAuditLog.log_event(
            event_type='connection_deleted',
            message=f'SSO connection deleted: {instance.name}',
            connection=instance,
            organization=instance.organization,
            user=self.request.user,
            severity='warning'
        )

        instance.delete()

    @action(detail=True, methods=['post'])
    def test(self, request, pk=None):
        """
        Test SSO connection.
        """
        connection = self.get_object()

        try:
            # Generate test login URL
            if connection.provider.provider_type in ['oauth2', 'oidc']:
                if connection.provider.provider_type == 'oidc':
                    service = OIDCService(connection)
                else:
                    service = OAuth2Service(connection)

                result = service.get_authorization_url(
                    redirect_uri=connection.redirect_uri
                )

                SSOAuditLog.log_event(
                    event_type='connection_tested',
                    message=f'SSO connection tested: {connection.name}',
                    connection=connection,
                    organization=connection.organization,
                    user=request.user,
                    severity='info'
                )

                return Response({
                    'status': 'success',
                    'test_url': result['authorization_url'],
                    'message': 'Test login URL generated successfully'
                })

            elif connection.provider.provider_type == 'saml2':
                service = SAMLService(connection)
                sso_url = service.initiate_login()

                SSOAuditLog.log_event(
                    event_type='connection_tested',
                    message=f'SAML connection tested: {connection.name}',
                    connection=connection,
                    organization=connection.organization,
                    user=request.user,
                    severity='info'
                )

                return Response({
                    'status': 'success',
                    'test_url': sso_url,
                    'message': 'SAML test login URL generated successfully'
                })

        except Exception as e:
            SSOAuditLog.log_event(
                event_type='configuration_error',
                message=f'SSO connection test failed: {str(e)}',
                connection=connection,
                organization=connection.organization,
                user=request.user,
                severity='error',
                error_code='CONNECTION_TEST_FAILED',
                error_details={'error': str(e)}
            )

            return Response(
                {'error': f'Connection test failed: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['get'])
    def stats(self, request, pk=None):
        """
        Get connection statistics.
        """
        connection = self.get_object()

        # Count total logins
        total_logins = SSOAuditLog.objects.filter(
            connection=connection,
            event_type__in=['login_success', 'login_failure']
        ).count()

        # Count successful logins
        successful_logins = SSOAuditLog.objects.filter(
            connection=connection,
            event_type='login_success'
        ).count()

        # Count failed logins
        failed_logins = SSOAuditLog.objects.filter(
            connection=connection,
            event_type='login_failure'
        ).count()

        # Count active sessions
        active_sessions = SSOSession.objects.filter(
            connection=connection,
            is_active=True
        ).count()

        # Count unique users
        unique_users = SSOSession.objects.filter(
            connection=connection
        ).values('user').distinct().count()

        # Get last login
        last_login = SSOAuditLog.objects.filter(
            connection=connection,
            event_type='login_success'
        ).order_by('-created_at').first()

        data = {
            'total_logins': total_logins,
            'successful_logins': successful_logins,
            'failed_logins': failed_logins,
            'active_sessions': active_sessions,
            'unique_users': unique_users,
            'last_login_at': last_login.created_at if last_login else None
        }

        serializer = SSOConnectionStatsSerializer(data)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """Activate SSO connection."""
        connection = self.get_object()
        connection.status = 'active'
        connection.save()

        SSOAuditLog.log_event(
            event_type='connection_updated',
            message=f'SSO connection activated: {connection.name}',
            connection=connection,
            organization=connection.organization,
            user=request.user,
            severity='info'
        )

        return Response({'status': 'Connection activated'})

    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """Deactivate SSO connection."""
        connection = self.get_object()
        connection.status = 'inactive'
        connection.save()

        # Deactivate all sessions
        SSOSession.objects.filter(connection=connection, is_active=True).update(
            is_active=False
        )

        SSOAuditLog.log_event(
            event_type='connection_updated',
            message=f'SSO connection deactivated: {connection.name}',
            connection=connection,
            organization=connection.organization,
            user=request.user,
            severity='warning'
        )

        return Response({'status': 'Connection deactivated'})


class SSOSessionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for SSO sessions.
    Read-only for monitoring and auditing.
    """
    queryset = SSOSession.objects.all()
    serializer_class = SSOSessionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Filter sessions."""
        queryset = super().get_queryset()

        # Filter by user (own sessions or all if admin)
        if not self.request.user.is_superuser:
            queryset = queryset.filter(user=self.request.user)

        # Filter by organization if provided
        organization_id = self.request.query_params.get('organization_id')
        if organization_id:
            queryset = queryset.filter(connection__organization_id=organization_id)

        # Filter by active status
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')

        return queryset.select_related('user', 'connection', 'connection__provider')

    @action(detail=True, methods=['post'])
    def revoke(self, request, pk=None):
        """Revoke SSO session."""
        session = self.get_object()

        # Check if user can revoke this session
        if not request.user.is_superuser and session.user != request.user:
            raise PermissionDenied('You can only revoke your own sessions')

        SSOSessionService.invalidate_session(session)

        return Response({'status': 'Session revoked'})


class SSOAuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for SSO audit logs.
    Read-only for compliance and security monitoring.
    """
    queryset = SSOAuditLog.objects.all()
    serializer_class = SSOAuditLogSerializer
    permission_classes = [permissions.IsAuthenticated, IsOrganizationAdmin]

    def get_queryset(self):
        """Filter audit logs."""
        queryset = super().get_queryset()

        # Filter by organization
        organization_id = self.request.query_params.get('organization_id')
        if organization_id:
            queryset = queryset.filter(organization_id=organization_id)

        # Filter by event type
        event_type = self.request.query_params.get('event_type')
        if event_type:
            queryset = queryset.filter(event_type=event_type)

        # Filter by severity
        severity = self.request.query_params.get('severity')
        if severity:
            queryset = queryset.filter(severity=severity)

        # Filter by user
        user_id = self.request.query_params.get('user_id')
        if user_id:
            queryset = queryset.filter(user_id=user_id)

        # Filter by email
        email = self.request.query_params.get('email')
        if email:
            queryset = queryset.filter(email=email)

        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        if start_date:
            queryset = queryset.filter(created_at__gte=start_date)

        end_date = self.request.query_params.get('end_date')
        if end_date:
            queryset = queryset.filter(created_at__lte=end_date)

        return queryset.select_related('user', 'connection', 'organization')


class SSOLoginView(APIView):
    """
    Initiate SSO login flow.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        """
        Initiate SSO login.

        Returns authorization URL for OAuth/OIDC or redirects for SAML.
        """
        serializer = SSOInitiateLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        connection_id = serializer.validated_data['connection_id']
        redirect_uri = serializer.validated_data['redirect_uri']

        try:
            connection = SSOConnection.objects.select_related('provider').get(
                id=connection_id
            )

            if connection.provider.provider_type in ['oauth2', 'oidc']:
                # OAuth/OIDC flow
                if connection.provider.provider_type == 'oidc':
                    service = OIDCService(connection)
                else:
                    service = OAuth2Service(connection)

                result = service.get_authorization_url(redirect_uri)

                return Response({
                    'authorization_url': result['authorization_url'],
                    'state': result['state']
                })

            elif connection.provider.provider_type == 'saml2':
                # SAML flow
                service = SAMLService(connection)
                sso_url = service.initiate_login()

                return Response({
                    'authorization_url': sso_url
                })

        except SSOConnection.DoesNotExist:
            return Response(
                {'error': 'SSO connection not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            SSOAuditLog.log_event(
                event_type='authentication_error',
                message=f'SSO login initiation failed: {str(e)}',
                connection=connection,
                organization=connection.organization,
                ip_address=request.META.get('REMOTE_ADDR'),
                severity='error',
                error_code='LOGIN_INITIATION_FAILED',
                error_details={'error': str(e)}
            )

            return Response(
                {'error': f'Failed to initiate SSO login: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )


class SSOCallbackView(APIView):
    """
    Handle SSO callback (OAuth/OIDC).
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        """Handle OAuth/OIDC callback."""
        code = request.query_params.get('code')
        state = request.query_params.get('state')
        error = request.query_params.get('error')

        if error:
            return Response(
                {
                    'error': error,
                    'error_description': request.query_params.get('error_description', '')
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        if not code or not state:
            return Response(
                {'error': 'Missing code or state parameter'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Get state token
            state_token = SSOStateToken.objects.select_related(
                'connection', 'connection__provider', 'connection__organization'
            ).get(state=state, is_used=False)

            if not state_token.is_valid():
                raise ValidationError('State token expired')

            connection = state_token.connection

            # Exchange code for tokens
            if connection.provider.provider_type == 'oidc':
                service = OIDCService(connection)
            else:
                service = OAuth2Service(connection)

            tokens = service.exchange_code_for_tokens(
                code=code,
                redirect_uri=state_token.redirect_uri,
                state=state,
                code_verifier=state_token.code_verifier
            )

            # Get user info
            user_info = service.get_user_info(tokens['access_token'])

            # Provision user
            provisioning_service = UserProvisioningService(connection)
            user, created = provisioning_service.provision_user(
                user_info=user_info,
                ip_address=request.META.get('REMOTE_ADDR')
            )

            # Create SSO session
            sso_session = SSOSessionService.create_session(
                user=user,
                connection=connection,
                tokens=tokens,
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT')
            )

            # Generate JWT tokens for FlowPilot
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)

            return Response({
                'access_token': access_token,
                'refresh_token': refresh_token,
                'user': {
                    'id': str(user.id),
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name
                },
                'sso_session_id': str(sso_session.id)
            })

        except SSOStateToken.DoesNotExist:
            return Response(
                {'error': 'Invalid state parameter'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': f'SSO callback failed: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )


class SAMLACSView(APIView):
    """
    SAML Assertion Consumer Service (ACS).
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        """Handle SAML response."""
        saml_response = request.POST.get('SAMLResponse')
        relay_state = request.POST.get('RelayState')

        if not saml_response:
            return Response(
                {'error': 'Missing SAML response'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Get connection from relay state or other mechanism
            # This is simplified - in production, you'd track the relay state
            connection_id = request.session.get('saml_connection_id')
            connection = SSOConnection.objects.select_related(
                'provider', 'organization'
            ).get(id=connection_id)

            # Process SAML response
            service = SAMLService(connection)
            saml_data = service.process_response(saml_response)

            # Build user info from SAML attributes
            user_info = {}
            for attr_name, attr_value in saml_data['attributes'].items():
                user_info[attr_name] = attr_value[0] if isinstance(attr_value, list) else attr_value

            # Add name_id as email fallback
            if 'email' not in user_info:
                user_info['email'] = saml_data['name_id']

            # Provision user
            provisioning_service = UserProvisioningService(connection)
            user, created = provisioning_service.provision_user(
                user_info=user_info,
                ip_address=request.META.get('REMOTE_ADDR')
            )

            # Create SSO session
            sso_session = SSOSessionService.create_session(
                user=user,
                connection=connection,
                tokens={'access_token': ''},  # SAML doesn't use access tokens
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT')
            )

            # Store SAML session info
            sso_session.idp_session_id = saml_data.get('session_index')
            sso_session.save()

            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)

            # Redirect to frontend with tokens
            frontend_url = f"{request.scheme}://{request.get_host()}/sso/callback"
            return redirect(f"{frontend_url}?access_token={access_token}&refresh_token={refresh_token}")

        except Exception as e:
            return Response(
                {'error': f'SAML ACS failed: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )


class SAMLMetadataView(APIView):
    """
    SAML Service Provider Metadata.
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request, connection_id):
        """Return SAML SP metadata XML."""
        try:
            connection = SSOConnection.objects.select_related('provider').get(
                id=connection_id
            )

            if connection.provider.provider_type != 'saml2':
                return Response(
                    {'error': 'Connection is not SAML 2.0'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            service = SAMLService(connection)
            settings = service.get_saml_settings()

            # Generate metadata XML
            from onelogin.saml2.settings import OneLogin_Saml2_Settings
            saml_settings = OneLogin_Saml2_Settings(settings)
            metadata = saml_settings.get_sp_metadata()

            return Response(metadata, content_type='application/xml')

        except SSOConnection.DoesNotExist:
            return Response(
                {'error': 'SSO connection not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': f'Failed to generate metadata: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
