"""
Tests for SSO models.
"""
from django.test import TestCase
from django.utils import timezone
from datetime import timedelta

from apps.users.models import User
from apps.organizations.models import Organization
from apps.sso.models import (
    SSOProvider, SSOConnection, SSOSession,
    SSOAuditLog, SSOStateToken
)


class SSOProviderModelTest(TestCase):
    """Tests for SSOProvider model."""

    def setUp(self):
        """Set up test data."""
        self.provider = SSOProvider.objects.create(
            name='google_sso',
            provider_type='oidc',
            provider_name='google',
            display_name='Google Workspace',
            is_enabled=True,
            authorization_url='https://accounts.google.com/o/oauth2/v2/auth',
            token_url='https://oauth2.googleapis.com/token',
            userinfo_url='https://openidconnect.googleapis.com/v1/userinfo',
            scopes=['openid', 'email', 'profile']
        )

    def test_provider_creation(self):
        """Test provider creation."""
        self.assertEqual(self.provider.name, 'google_sso')
        self.assertEqual(self.provider.provider_type, 'oidc')
        self.assertTrue(self.provider.is_enabled)

    def test_provider_string_representation(self):
        """Test provider string representation."""
        self.assertEqual(str(self.provider), 'Google Workspace')


class SSOConnectionModelTest(TestCase):
    """Tests for SSOConnection model."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            email='admin@example.com',
            password='testpass123',
            first_name='Admin',
            last_name='User'
        )

        self.organization = Organization.objects.create(
            name='Test Organization',
            slug='test-org'
        )

        self.provider = SSOProvider.objects.create(
            name='google_sso',
            provider_type='oidc',
            provider_name='google',
            display_name='Google Workspace',
            is_enabled=True
        )

        self.connection = SSOConnection.objects.create(
            organization=self.organization,
            provider=self.provider,
            name='Google SSO',
            client_id='test-client-id',
            client_secret_encrypted='test-secret',
            status='active',
            auto_provision_users=True,
            created_by=self.user
        )

    def test_connection_creation(self):
        """Test connection creation."""
        self.assertEqual(self.connection.name, 'Google SSO')
        self.assertEqual(self.connection.status, 'active')
        self.assertTrue(self.connection.auto_provision_users)

    def test_is_active_property(self):
        """Test is_active property."""
        self.assertTrue(self.connection.is_active)

        self.connection.status = 'inactive'
        self.assertFalse(self.connection.is_active)


class SSOSessionModelTest(TestCase):
    """Tests for SSOSession model."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            email='user@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )

        self.organization = Organization.objects.create(
            name='Test Organization',
            slug='test-org'
        )

        self.provider = SSOProvider.objects.create(
            name='google_sso',
            provider_type='oidc',
            provider_name='google',
            display_name='Google Workspace',
            is_enabled=True
        )

        self.connection = SSOConnection.objects.create(
            organization=self.organization,
            provider=self.provider,
            name='Google SSO',
            client_id='test-client-id',
            status='active',
            created_by=self.user
        )

        self.session = SSOSession.objects.create(
            user=self.user,
            connection=self.connection,
            session_id='test-session-id',
            access_token_encrypted='test-token',
            expires_at=timezone.now() + timedelta(days=7),
            is_active=True
        )

    def test_session_creation(self):
        """Test session creation."""
        self.assertEqual(self.session.user, self.user)
        self.assertEqual(self.session.connection, self.connection)
        self.assertTrue(self.session.is_active)

    def test_is_expired(self):
        """Test is_expired method."""
        self.assertFalse(self.session.is_expired())

        # Set expiration to past
        self.session.expires_at = timezone.now() - timedelta(hours=1)
        self.assertTrue(self.session.is_expired())


class SSOStateTokenModelTest(TestCase):
    """Tests for SSOStateToken model."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            email='user@example.com',
            password='testpass123'
        )

        self.organization = Organization.objects.create(
            name='Test Organization',
            slug='test-org'
        )

        self.provider = SSOProvider.objects.create(
            name='google_sso',
            provider_type='oidc',
            provider_name='google',
            display_name='Google Workspace',
            is_enabled=True
        )

        self.connection = SSOConnection.objects.create(
            organization=self.organization,
            provider=self.provider,
            name='Google SSO',
            client_id='test-client-id',
            status='active',
            created_by=self.user
        )

        self.token = SSOStateToken.objects.create(
            token='test-token',
            state='test-state',
            connection=self.connection,
            expires_at=timezone.now() + timedelta(minutes=10)
        )

    def test_token_creation(self):
        """Test token creation."""
        self.assertEqual(self.token.token, 'test-token')
        self.assertEqual(self.token.state, 'test-state')
        self.assertFalse(self.token.is_used)

    def test_is_valid(self):
        """Test is_valid method."""
        self.assertTrue(self.token.is_valid())

        # Mark as used
        self.token.is_used = True
        self.assertFalse(self.token.is_valid())

        # Set expiration to past
        self.token.is_used = False
        self.token.expires_at = timezone.now() - timedelta(minutes=1)
        self.assertFalse(self.token.is_valid())

    def test_generate_token(self):
        """Test generate_token method."""
        token = SSOStateToken.generate_token()
        self.assertIsInstance(token, str)
        self.assertGreater(len(token), 20)

    def test_generate_state(self):
        """Test generate_state method."""
        state = SSOStateToken.generate_state()
        self.assertIsInstance(state, str)
        self.assertGreater(len(state), 20)

    def test_generate_pkce_pair(self):
        """Test generate_pkce_pair method."""
        verifier, challenge = SSOStateToken.generate_pkce_pair()
        self.assertIsInstance(verifier, str)
        self.assertIsInstance(challenge, str)
        self.assertGreater(len(verifier), 40)
        self.assertGreater(len(challenge), 40)


class SSOAuditLogModelTest(TestCase):
    """Tests for SSOAuditLog model."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            email='user@example.com',
            password='testpass123'
        )

        self.organization = Organization.objects.create(
            name='Test Organization',
            slug='test-org'
        )

    def test_log_event(self):
        """Test log_event class method."""
        log = SSOAuditLog.log_event(
            event_type='login_success',
            message='User logged in successfully',
            user=self.user,
            organization=self.organization,
            severity='info'
        )

        self.assertEqual(log.event_type, 'login_success')
        self.assertEqual(log.user, self.user)
        self.assertEqual(log.organization, self.organization)
        self.assertEqual(log.severity, 'info')
