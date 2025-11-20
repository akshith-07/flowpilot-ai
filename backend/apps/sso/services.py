"""
SSO services for OAuth 2.0, OIDC, and SAML 2.0 authentication.
"""
import secrets
import hashlib
import base64
import json
import urllib.parse
from datetime import timedelta
from typing import Dict, Optional, Tuple, Any

import requests
from django.conf import settings
from django.utils import timezone
from django.db import transaction
from rest_framework.exceptions import ValidationError, AuthenticationFailed

from apps.users.models import User
from apps.organizations.models import Organization, OrganizationMember, Role
from .models import (
    SSOConnection, SSOSession, SSOAuditLog,
    SSOStateToken, SSOProvider
)


class OAuth2Service:
    """
    Service for handling OAuth 2.0 flows.
    Supports authorization code flow with PKCE.
    """

    def __init__(self, connection: SSOConnection):
        """
        Initialize OAuth2 service.

        Args:
            connection: SSOConnection instance
        """
        self.connection = connection
        self.provider = connection.provider

    def get_authorization_url(self, redirect_uri: str, state: Optional[str] = None) -> Dict[str, str]:
        """
        Generate authorization URL for OAuth 2.0 flow.

        Args:
            redirect_uri: Redirect URI after authorization
            state: Optional state parameter

        Returns:
            dict: Contains authorization_url, state, code_verifier (if PKCE)
        """
        if not state:
            state = SSOStateToken.generate_state()

        # Generate PKCE parameters if required
        code_verifier = None
        code_challenge = None
        if self.connection.pkce_required:
            code_verifier, code_challenge = SSOStateToken.generate_pkce_pair()

        # Create state token
        state_token = SSOStateToken.objects.create(
            token=SSOStateToken.generate_token(),
            state=state,
            code_verifier=code_verifier,
            code_challenge=code_challenge,
            connection=self.connection,
            redirect_uri=redirect_uri,
            expires_at=timezone.now() + timedelta(minutes=10)
        )

        # Build authorization URL
        params = {
            'client_id': self.connection.client_id,
            'redirect_uri': redirect_uri,
            'response_type': 'code',
            'state': state,
            'scope': ' '.join(self.provider.scopes) if self.provider.scopes else 'openid email profile',
        }

        if code_challenge:
            params['code_challenge'] = code_challenge
            params['code_challenge_method'] = 'S256'

        authorization_url = f"{self.provider.authorization_url}?{urllib.parse.urlencode(params)}"

        # Log event
        SSOAuditLog.log_event(
            event_type='login_initiated',
            message=f'OAuth2 login initiated for {self.provider.display_name}',
            connection=self.connection,
            organization=self.connection.organization,
            provider_name=self.provider.display_name,
            severity='info'
        )

        return {
            'authorization_url': authorization_url,
            'state': state,
            'code_verifier': code_verifier
        }

    def exchange_code_for_tokens(
        self,
        code: str,
        redirect_uri: str,
        state: str,
        code_verifier: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Exchange authorization code for access tokens.

        Args:
            code: Authorization code
            redirect_uri: Redirect URI used in authorization request
            state: State parameter
            code_verifier: PKCE code verifier

        Returns:
            dict: Token response
        """
        # Validate state token
        try:
            state_token = SSOStateToken.objects.get(
                state=state,
                connection=self.connection,
                is_used=False
            )
            if not state_token.is_valid():
                raise ValidationError('State token expired or invalid')

            # Mark state token as used
            state_token.is_used = True
            state_token.used_at = timezone.now()
            state_token.save()

        except SSOStateToken.DoesNotExist:
            SSOAuditLog.log_event(
                event_type='authentication_error',
                message='Invalid state token',
                connection=self.connection,
                organization=self.connection.organization,
                provider_name=self.provider.display_name,
                severity='error',
                error_code='INVALID_STATE'
            )
            raise ValidationError('Invalid state parameter')

        # Prepare token request
        token_data = {
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': redirect_uri,
            'client_id': self.connection.client_id,
            'client_secret': self.connection.client_secret_encrypted,
        }

        # Add PKCE code verifier if required
        if self.connection.pkce_required and code_verifier:
            token_data['code_verifier'] = code_verifier

        # Exchange code for tokens
        try:
            response = requests.post(
                self.provider.token_url,
                data=token_data,
                headers={'Accept': 'application/json'},
                timeout=30
            )
            response.raise_for_status()
            tokens = response.json()

            SSOAuditLog.log_event(
                event_type='token_issued',
                message='Access token issued successfully',
                connection=self.connection,
                organization=self.connection.organization,
                provider_name=self.provider.display_name,
                severity='info'
            )

            return tokens

        except requests.RequestException as e:
            SSOAuditLog.log_event(
                event_type='token_error',
                message=f'Token exchange failed: {str(e)}',
                connection=self.connection,
                organization=self.connection.organization,
                provider_name=self.provider.display_name,
                severity='error',
                error_code='TOKEN_EXCHANGE_FAILED',
                error_details={'error': str(e)}
            )
            raise AuthenticationFailed('Failed to exchange authorization code')

    def get_user_info(self, access_token: str) -> Dict[str, Any]:
        """
        Get user information from provider using access token.

        Args:
            access_token: OAuth access token

        Returns:
            dict: User information
        """
        try:
            response = requests.get(
                self.provider.userinfo_url,
                headers={
                    'Authorization': f'Bearer {access_token}',
                    'Accept': 'application/json'
                },
                timeout=30
            )
            response.raise_for_status()
            return response.json()

        except requests.RequestException as e:
            SSOAuditLog.log_event(
                event_type='authentication_error',
                message=f'Failed to fetch user info: {str(e)}',
                connection=self.connection,
                organization=self.connection.organization,
                provider_name=self.provider.display_name,
                severity='error',
                error_code='USERINFO_FAILED',
                error_details={'error': str(e)}
            )
            raise AuthenticationFailed('Failed to fetch user information')

    def refresh_access_token(self, refresh_token: str) -> Dict[str, Any]:
        """
        Refresh access token using refresh token.

        Args:
            refresh_token: OAuth refresh token

        Returns:
            dict: New token response
        """
        token_data = {
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token,
            'client_id': self.connection.client_id,
            'client_secret': self.connection.client_secret_encrypted,
        }

        try:
            response = requests.post(
                self.provider.token_url,
                data=token_data,
                headers={'Accept': 'application/json'},
                timeout=30
            )
            response.raise_for_status()
            tokens = response.json()

            SSOAuditLog.log_event(
                event_type='token_refreshed',
                message='Access token refreshed successfully',
                connection=self.connection,
                organization=self.connection.organization,
                provider_name=self.provider.display_name,
                severity='info'
            )

            return tokens

        except requests.RequestException as e:
            SSOAuditLog.log_event(
                event_type='token_error',
                message=f'Token refresh failed: {str(e)}',
                connection=self.connection,
                organization=self.connection.organization,
                provider_name=self.provider.display_name,
                severity='error',
                error_code='TOKEN_REFRESH_FAILED',
                error_details={'error': str(e)}
            )
            raise AuthenticationFailed('Failed to refresh access token')


class OIDCService(OAuth2Service):
    """
    Service for handling OpenID Connect flows.
    Extends OAuth2Service with OIDC-specific functionality.
    """

    def get_authorization_url(self, redirect_uri: str, state: Optional[str] = None) -> Dict[str, str]:
        """
        Generate authorization URL for OIDC flow.

        Args:
            redirect_uri: Redirect URI after authorization
            state: Optional state parameter

        Returns:
            dict: Contains authorization_url, state, nonce, code_verifier (if PKCE)
        """
        result = super().get_authorization_url(redirect_uri, state)

        # Add nonce for OIDC
        nonce = SSOStateToken.generate_nonce()

        # Update state token with nonce
        state_token = SSOStateToken.objects.get(state=result['state'])
        state_token.nonce = nonce
        state_token.save()

        # Add nonce to URL
        result['authorization_url'] += f'&nonce={nonce}'
        result['nonce'] = nonce

        return result

    def verify_id_token(self, id_token: str, nonce: str) -> Dict[str, Any]:
        """
        Verify and decode ID token.

        Args:
            id_token: JWT ID token
            nonce: Nonce used in authorization request

        Returns:
            dict: Decoded token claims
        """
        try:
            import jwt
            from jwt import PyJWKClient

            # Get JWKS
            jwks_client = PyJWKClient(self.provider.jwks_url)
            signing_key = jwks_client.get_signing_key_from_jwt(id_token)

            # Verify and decode token
            claims = jwt.decode(
                id_token,
                signing_key.key,
                algorithms=['RS256'],
                audience=self.connection.client_id,
                options={'verify_exp': True}
            )

            # Verify nonce
            if claims.get('nonce') != nonce:
                raise ValidationError('Invalid nonce')

            return claims

        except Exception as e:
            SSOAuditLog.log_event(
                event_type='token_error',
                message=f'ID token verification failed: {str(e)}',
                connection=self.connection,
                organization=self.connection.organization,
                provider_name=self.provider.display_name,
                severity='error',
                error_code='ID_TOKEN_VERIFICATION_FAILED',
                error_details={'error': str(e)}
            )
            raise AuthenticationFailed('Invalid ID token')


class SAMLService:
    """
    Service for handling SAML 2.0 authentication.
    """

    def __init__(self, connection: SSOConnection):
        """
        Initialize SAML service.

        Args:
            connection: SSOConnection instance
        """
        self.connection = connection
        self.provider = connection.provider

    def get_saml_settings(self) -> Dict[str, Any]:
        """
        Get SAML settings for python3-saml library.

        Returns:
            dict: SAML settings
        """
        return {
            'strict': True,
            'debug': settings.DEBUG,
            'sp': {
                'entityId': self.connection.sp_entity_id,
                'assertionConsumerService': {
                    'url': self.connection.acs_url,
                    'binding': 'urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST'
                },
                'singleLogoutService': {
                    'url': f"{settings.BACKEND_URL}/api/v1/sso/saml/slo/",
                    'binding': 'urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect'
                },
                'NameIDFormat': 'urn:oasis:names:tc:SAML:1.1:nameid-format:emailAddress',
                'x509cert': '',  # SP certificate (optional)
                'privateKey': ''  # SP private key (optional)
            },
            'idp': {
                'entityId': self.provider.entity_id,
                'singleSignOnService': {
                    'url': self.provider.sso_url,
                    'binding': 'urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect'
                },
                'singleLogoutService': {
                    'url': self.provider.slo_url,
                    'binding': 'urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect'
                },
                'x509cert': self.connection.idp_certificate
            }
        }

    def initiate_login(self) -> str:
        """
        Initiate SAML login request.

        Returns:
            str: SAML authentication request URL
        """
        try:
            from onelogin.saml2.auth import OneLogin_Saml2_Auth
            from onelogin.saml2.utils import OneLogin_Saml2_Utils

            saml_auth = OneLogin_Saml2_Auth(
                {},
                self.get_saml_settings()
            )

            # Build authentication request
            sso_url = saml_auth.login(return_to=self.connection.acs_url)

            SSOAuditLog.log_event(
                event_type='login_initiated',
                message=f'SAML login initiated for {self.provider.display_name}',
                connection=self.connection,
                organization=self.connection.organization,
                provider_name=self.provider.display_name,
                severity='info'
            )

            return sso_url

        except Exception as e:
            SSOAuditLog.log_event(
                event_type='authentication_error',
                message=f'SAML login initiation failed: {str(e)}',
                connection=self.connection,
                organization=self.connection.organization,
                provider_name=self.provider.display_name,
                severity='error',
                error_code='SAML_LOGIN_FAILED',
                error_details={'error': str(e)}
            )
            raise ValidationError('Failed to initiate SAML login')

    def process_response(self, saml_response: str) -> Dict[str, Any]:
        """
        Process SAML response and extract user attributes.

        Args:
            saml_response: Base64-encoded SAML response

        Returns:
            dict: User attributes
        """
        try:
            from onelogin.saml2.auth import OneLogin_Saml2_Auth

            saml_auth = OneLogin_Saml2_Auth(
                {
                    'http_host': '',
                    'script_name': '',
                    'post_data': {'SAMLResponse': saml_response}
                },
                self.get_saml_settings()
            )

            # Process response
            saml_auth.process_response()

            errors = saml_auth.get_errors()
            if errors:
                error_reason = saml_auth.get_last_error_reason()
                SSOAuditLog.log_event(
                    event_type='authentication_error',
                    message=f'SAML response validation failed: {error_reason}',
                    connection=self.connection,
                    organization=self.connection.organization,
                    provider_name=self.provider.display_name,
                    severity='error',
                    error_code='SAML_VALIDATION_FAILED',
                    error_details={'errors': errors, 'reason': error_reason}
                )
                raise AuthenticationFailed('Invalid SAML response')

            # Check authentication status
            if not saml_auth.is_authenticated():
                raise AuthenticationFailed('SAML authentication failed')

            # Extract attributes
            attributes = saml_auth.get_attributes()
            name_id = saml_auth.get_nameid()
            session_index = saml_auth.get_session_index()

            return {
                'name_id': name_id,
                'session_index': session_index,
                'attributes': attributes
            }

        except AuthenticationFailed:
            raise
        except Exception as e:
            SSOAuditLog.log_event(
                event_type='authentication_error',
                message=f'SAML response processing failed: {str(e)}',
                connection=self.connection,
                organization=self.connection.organization,
                provider_name=self.provider.display_name,
                severity='error',
                error_code='SAML_PROCESSING_FAILED',
                error_details={'error': str(e)}
            )
            raise AuthenticationFailed('Failed to process SAML response')


class UserProvisioningService:
    """
    Service for automatic user provisioning from SSO.
    """

    def __init__(self, connection: SSOConnection):
        """
        Initialize provisioning service.

        Args:
            connection: SSOConnection instance
        """
        self.connection = connection

    @transaction.atomic
    def provision_user(
        self,
        user_info: Dict[str, Any],
        ip_address: Optional[str] = None
    ) -> Tuple[User, bool]:
        """
        Provision user from SSO user info.

        Args:
            user_info: User information from SSO provider
            ip_address: IP address of the request

        Returns:
            tuple: (User instance, created flag)
        """
        # Extract email from user info
        email = self._extract_email(user_info)
        if not email:
            raise ValidationError('Email not found in SSO response')

        # Validate email domain if domain restrictions exist
        if self.connection.allowed_domains:
            domain = email.split('@')[1]
            if domain not in self.connection.allowed_domains:
                SSOAuditLog.log_event(
                    event_type='authentication_error',
                    message=f'Email domain {domain} not allowed',
                    connection=self.connection,
                    organization=self.connection.organization,
                    email=email,
                    severity='warning',
                    error_code='DOMAIN_NOT_ALLOWED'
                )
                raise ValidationError(f'Email domain {domain} is not allowed for this SSO connection')

        # Check if user exists
        try:
            user = User.objects.get(email=email)
            created = False

            # Update user info if auto-provisioning is enabled
            if self.connection.auto_provision_users:
                self._update_user_from_sso(user, user_info)

        except User.DoesNotExist:
            # Create new user if auto-provisioning is enabled
            if not self.connection.auto_provision_users:
                raise ValidationError('User does not exist and auto-provisioning is disabled')

            user = self._create_user_from_sso(email, user_info)
            created = True

        # Add user to organization if not already a member
        self._ensure_organization_membership(user, user_info)

        # Log provisioning event
        SSOAuditLog.log_event(
            event_type='user_provisioned' if created else 'user_updated',
            message=f'User {"created" if created else "updated"} via SSO',
            user=user,
            connection=self.connection,
            organization=self.connection.organization,
            email=email,
            ip_address=ip_address,
            severity='info'
        )

        return user, created

    def _extract_email(self, user_info: Dict[str, Any]) -> Optional[str]:
        """Extract email from user info using attribute mapping."""
        email_attr = self.connection.attribute_mapping.get('email', 'email')

        # Handle nested attributes (e.g., 'user.email')
        if '.' in email_attr:
            parts = email_attr.split('.')
            value = user_info
            for part in parts:
                value = value.get(part, {})
            return value

        return user_info.get(email_attr)

    def _extract_field(self, user_info: Dict[str, Any], field_name: str, default: str = '') -> str:
        """Extract field from user info using attribute mapping."""
        attr_name = self.connection.attribute_mapping.get(field_name, field_name)

        # Handle nested attributes
        if '.' in attr_name:
            parts = attr_name.split('.')
            value = user_info
            for part in parts:
                value = value.get(part, {})
            return value or default

        return user_info.get(attr_name, default)

    def _create_user_from_sso(self, email: str, user_info: Dict[str, Any]) -> User:
        """Create new user from SSO user info."""
        user = User.objects.create(
            email=email,
            first_name=self._extract_field(user_info, 'first_name', 'User'),
            last_name=self._extract_field(user_info, 'last_name', ''),
            avatar_url=self._extract_field(user_info, 'avatar_url', None),
            is_active=self.connection.auto_activate_users,
            email_verified=not self.connection.require_email_verification
        )

        # Set unusable password (SSO users don't need password)
        user.set_unusable_password()
        user.save()

        return user

    def _update_user_from_sso(self, user: User, user_info: Dict[str, Any]) -> None:
        """Update existing user from SSO user info."""
        updated = False

        # Update first name if provided
        first_name = self._extract_field(user_info, 'first_name')
        if first_name and user.first_name != first_name:
            user.first_name = first_name
            updated = True

        # Update last name if provided
        last_name = self._extract_field(user_info, 'last_name')
        if last_name and user.last_name != last_name:
            user.last_name = last_name
            updated = True

        # Update avatar if provided
        avatar_url = self._extract_field(user_info, 'avatar_url')
        if avatar_url and user.avatar_url != avatar_url:
            user.avatar_url = avatar_url
            updated = True

        if updated:
            user.save()

    def _ensure_organization_membership(self, user: User, user_info: Dict[str, Any]) -> None:
        """Ensure user is a member of the organization."""
        # Check if user is already a member
        if OrganizationMember.objects.filter(
            organization=self.connection.organization,
            user=user
        ).exists():
            return

        # Determine role from SSO groups
        role = self._determine_role(user_info)

        # Add user to organization
        OrganizationMember.objects.create(
            organization=self.connection.organization,
            user=user,
            role=role
        )

    def _determine_role(self, user_info: Dict[str, Any]) -> Role:
        """Determine user role from SSO groups/roles."""
        # Extract groups from user info
        groups_attr = self.connection.attribute_mapping.get('groups', 'groups')
        groups = user_info.get(groups_attr, [])

        # Map groups to roles using role_mapping
        for group in groups:
            if group in self.connection.role_mapping:
                role_name = self.connection.role_mapping[group]
                try:
                    return Role.objects.get(
                        organization=self.connection.organization,
                        name=role_name
                    )
                except Role.DoesNotExist:
                    pass

        # Default to 'Member' role
        try:
            return Role.objects.get(
                organization=self.connection.organization,
                name='Member'
            )
        except Role.DoesNotExist:
            # Create default Member role if it doesn't exist
            return Role.objects.create(
                organization=self.connection.organization,
                name='Member',
                description='Default member role',
                permissions={}
            )


class SSOSessionService:
    """
    Service for managing SSO sessions.
    """

    @staticmethod
    def create_session(
        user: User,
        connection: SSOConnection,
        tokens: Dict[str, Any],
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> SSOSession:
        """
        Create SSO session.

        Args:
            user: User instance
            connection: SSOConnection instance
            tokens: Token response from provider
            ip_address: IP address
            user_agent: User agent string

        Returns:
            SSOSession instance
        """
        session = SSOSession.objects.create(
            user=user,
            connection=connection,
            session_id=secrets.token_urlsafe(32),
            access_token_encrypted=tokens.get('access_token'),
            id_token_encrypted=tokens.get('id_token'),
            refresh_token_encrypted=tokens.get('refresh_token'),
            access_token_expires_at=timezone.now() + timedelta(seconds=tokens.get('expires_in', 3600)),
            expires_at=timezone.now() + timedelta(days=7),
            ip_address=ip_address,
            user_agent=user_agent,
            is_active=True
        )

        SSOAuditLog.log_event(
            event_type='login_success',
            message='SSO login successful',
            user=user,
            connection=connection,
            session=session,
            organization=connection.organization,
            email=user.email,
            ip_address=ip_address,
            provider_name=connection.provider.display_name,
            severity='info'
        )

        return session

    @staticmethod
    def invalidate_session(session: SSOSession) -> None:
        """
        Invalidate SSO session.

        Args:
            session: SSOSession instance
        """
        session.is_active = False
        session.save()

        SSOAuditLog.log_event(
            event_type='logout',
            message='SSO session invalidated',
            user=session.user,
            connection=session.connection,
            session=session,
            organization=session.connection.organization,
            email=session.user.email,
            provider_name=session.connection.provider.display_name,
            severity='info'
        )
