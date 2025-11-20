"""
Tests for SSO services.
"""
from unittest.mock import Mock, patch
from django.test import TestCase

from apps.users.models import User
from apps.organizations.models import Organization, Role
from apps.sso.models import SSOProvider, SSOConnection
from apps.sso.services import (
    OAuth2Service, UserProvisioningService
)


class OAuth2ServiceTest(TestCase):
    """Tests for OAuth2Service."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            email='admin@example.com',
            password='testpass123'
        )

        self.organization = Organization.objects.create(
            name='Test Organization',
            slug='test-org'
        )

        self.provider = SSOProvider.objects.create(
            name='google_sso',
            provider_type='oauth2',
            provider_name='google',
            display_name='Google',
            is_enabled=True,
            authorization_url='https://accounts.google.com/o/oauth2/v2/auth',
            token_url='https://oauth2.googleapis.com/token',
            userinfo_url='https://www.googleapis.com/oauth2/v1/userinfo',
            scopes=['openid', 'email', 'profile']
        )

        self.connection = SSOConnection.objects.create(
            organization=self.organization,
            provider=self.provider,
            name='Google SSO',
            client_id='test-client-id',
            client_secret_encrypted='test-secret',
            redirect_uri='http://localhost:3000/sso/callback',
            status='active',
            created_by=self.user
        )

        self.service = OAuth2Service(self.connection)

    def test_get_authorization_url(self):
        """Test get_authorization_url method."""
        result = self.service.get_authorization_url('http://localhost:3000/sso/callback')

        self.assertIn('authorization_url', result)
        self.assertIn('state', result)
        self.assertIn('https://accounts.google.com/o/oauth2/v2/auth', result['authorization_url'])
        self.assertIn('client_id=test-client-id', result['authorization_url'])


class UserProvisioningServiceTest(TestCase):
    """Tests for UserProvisioningService."""

    def setUp(self):
        """Set up test data."""
        self.admin = User.objects.create_user(
            email='admin@example.com',
            password='testpass123'
        )

        self.organization = Organization.objects.create(
            name='Test Organization',
            slug='test-org'
        )

        # Create default Member role
        self.member_role = Role.objects.create(
            organization=self.organization,
            name='Member',
            description='Default member role',
            permissions={}
        )

        self.provider = SSOProvider.objects.create(
            name='google_sso',
            provider_type='oidc',
            provider_name='google',
            display_name='Google',
            is_enabled=True
        )

        self.connection = SSOConnection.objects.create(
            organization=self.organization,
            provider=self.provider,
            name='Google SSO',
            client_id='test-client-id',
            status='active',
            auto_provision_users=True,
            auto_activate_users=True,
            allowed_domains=['example.com'],
            attribute_mapping={
                'email': 'email',
                'first_name': 'given_name',
                'last_name': 'family_name'
            },
            created_by=self.admin
        )

        self.service = UserProvisioningService(self.connection)

    def test_provision_new_user(self):
        """Test provisioning a new user."""
        user_info = {
            'email': 'newuser@example.com',
            'given_name': 'New',
            'family_name': 'User'
        }

        user, created = self.service.provision_user(user_info)

        self.assertTrue(created)
        self.assertEqual(user.email, 'newuser@example.com')
        self.assertEqual(user.first_name, 'New')
        self.assertEqual(user.last_name, 'User')
        self.assertTrue(user.is_active)

    def test_provision_existing_user(self):
        """Test provisioning an existing user."""
        # Create existing user
        existing_user = User.objects.create_user(
            email='existing@example.com',
            password='testpass123',
            first_name='Old',
            last_name='Name'
        )

        user_info = {
            'email': 'existing@example.com',
            'given_name': 'New',
            'family_name': 'Name'
        }

        user, created = self.service.provision_user(user_info)

        self.assertFalse(created)
        self.assertEqual(user.id, existing_user.id)
        self.assertEqual(user.first_name, 'New')  # Should be updated

    def test_domain_restriction(self):
        """Test domain restriction."""
        user_info = {
            'email': 'user@otherdomain.com',
            'given_name': 'Test',
            'family_name': 'User'
        }

        with self.assertRaises(Exception):
            self.service.provision_user(user_info)

    def test_extract_email(self):
        """Test email extraction."""
        user_info = {'email': 'test@example.com'}
        email = self.service._extract_email(user_info)
        self.assertEqual(email, 'test@example.com')

    def test_extract_field(self):
        """Test field extraction."""
        user_info = {
            'given_name': 'Test',
            'family_name': 'User'
        }

        first_name = self.service._extract_field(user_info, 'first_name', 'Default')
        last_name = self.service._extract_field(user_info, 'last_name', 'Default')

        self.assertEqual(first_name, 'Test')
        self.assertEqual(last_name, 'User')
