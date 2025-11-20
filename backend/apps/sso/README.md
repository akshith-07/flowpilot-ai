# FlowPilot AI - Enterprise SSO Module

## Overview

The SSO (Single Sign-On) module provides enterprise-grade authentication capabilities for FlowPilot AI, supporting OAuth 2.0, OpenID Connect (OIDC), and SAML 2.0 protocols.

## Features

### Authentication Protocols

- **OAuth 2.0** with PKCE (Proof Key for Code Exchange)
- **OpenID Connect (OIDC)** with ID token validation
- **SAML 2.0** Service Provider implementation

### Supported Identity Providers

- Google Workspace (OIDC)
- Microsoft Azure AD (OIDC)
- Okta (SAML 2.0 / OIDC)
- OneLogin (SAML 2.0 / OIDC)
- Auth0 (OIDC)
- Generic SAML 2.0 providers
- Generic OIDC providers

### Security Features

- PKCE for OAuth 2.0 flows
- State parameter validation (CSRF protection)
- Nonce validation for OIDC
- Token encryption at rest
- Comprehensive audit logging
- Domain restrictions
- IP address tracking
- Session management

### User Management

- **Automatic User Provisioning**: Create users on first SSO login
- **Attribute Mapping**: Map IdP attributes to FlowPilot user fields
- **Role Mapping**: Map IdP groups/roles to FlowPilot organization roles
- **Just-in-Time (JIT) Provisioning**: Update user info on each login
- **Domain Restrictions**: Restrict SSO access by email domain

## Architecture

### Models

- **SSOProvider**: Template for SSO providers (Google, Microsoft, etc.)
- **SSOConnection**: Organization-specific SSO configuration
- **SSOSession**: Tracks active SSO sessions with tokens
- **SSOAuditLog**: Comprehensive audit trail for compliance
- **SSOStateToken**: Temporary tokens for OAuth/OIDC flows

### Services

- **OAuth2Service**: Handles OAuth 2.0 authorization code flow
- **OIDCService**: Extends OAuth2Service with OIDC functionality
- **SAMLService**: Handles SAML 2.0 authentication
- **UserProvisioningService**: Manages user creation and updates
- **SSOSessionService**: Manages SSO session lifecycle

## API Endpoints

### SSO Providers

```
GET    /api/v1/sso/providers/              # List available providers
GET    /api/v1/sso/providers/{id}/         # Get provider details
GET    /api/v1/sso/providers/available/    # Get available providers for org
```

### SSO Connections

```
GET    /api/v1/sso/connections/            # List connections
POST   /api/v1/sso/connections/            # Create connection
GET    /api/v1/sso/connections/{id}/       # Get connection details
PUT    /api/v1/sso/connections/{id}/       # Update connection
DELETE /api/v1/sso/connections/{id}/       # Delete connection
POST   /api/v1/sso/connections/{id}/test/  # Test connection
GET    /api/v1/sso/connections/{id}/stats/ # Get connection statistics
POST   /api/v1/sso/connections/{id}/activate/   # Activate connection
POST   /api/v1/sso/connections/{id}/deactivate/ # Deactivate connection
```

### SSO Authentication

```
POST   /api/v1/sso/login/                  # Initiate SSO login
GET    /api/v1/sso/callback/               # OAuth/OIDC callback
POST   /api/v1/sso/saml/acs/               # SAML Assertion Consumer Service
GET    /api/v1/sso/saml/metadata/{id}/     # Get SAML SP metadata
```

### SSO Sessions

```
GET    /api/v1/sso/sessions/               # List SSO sessions
GET    /api/v1/sso/sessions/{id}/          # Get session details
POST   /api/v1/sso/sessions/{id}/revoke/   # Revoke session
```

### SSO Audit Logs

```
GET    /api/v1/sso/audit-logs/             # List audit logs
GET    /api/v1/sso/audit-logs/{id}/        # Get audit log details
```

## Configuration

### Google Workspace (OIDC)

1. Create OAuth 2.0 credentials in Google Cloud Console
2. Configure authorized redirect URIs
3. Create SSO connection in FlowPilot:

```json
{
  "provider": "google",
  "client_id": "your-client-id.apps.googleusercontent.com",
  "client_secret": "your-client-secret",
  "redirect_uri": "https://your-domain.com/sso/callback",
  "allowed_domains": ["yourcompany.com"],
  "auto_provision_users": true,
  "attribute_mapping": {
    "email": "email",
    "first_name": "given_name",
    "last_name": "family_name",
    "avatar_url": "picture"
  }
}
```

### Microsoft Azure AD (OIDC)

1. Register application in Azure AD
2. Configure redirect URIs
3. Create SSO connection:

```json
{
  "provider": "microsoft",
  "client_id": "your-application-id",
  "client_secret": "your-client-secret",
  "redirect_uri": "https://your-domain.com/sso/callback",
  "allowed_domains": ["yourcompany.com"],
  "auto_provision_users": true,
  "attribute_mapping": {
    "email": "email",
    "first_name": "given_name",
    "last_name": "family_name"
  }
}
```

### SAML 2.0 (Okta, OneLogin, etc.)

1. Configure FlowPilot as SAML Service Provider in your IdP
2. Download IdP metadata XML
3. Create SSO connection:

```json
{
  "provider": "okta",
  "sp_entity_id": "https://your-domain.com/sso/saml",
  "acs_url": "https://your-domain.com/api/v1/sso/saml/acs/",
  "idp_metadata_url": "https://your-idp.com/metadata",
  "auto_provision_users": true,
  "attribute_mapping": {
    "email": "email",
    "first_name": "firstName",
    "last_name": "lastName",
    "groups": "groups"
  },
  "role_mapping": {
    "Admins": "Admin",
    "Users": "Member"
  }
}
```

## User Provisioning

### Attribute Mapping

Map IdP attributes to FlowPilot user fields:

```python
attribute_mapping = {
    'email': 'email',           # Required
    'first_name': 'given_name',
    'last_name': 'family_name',
    'avatar_url': 'picture',
    'groups': 'groups'          # For role mapping
}
```

### Role Mapping

Map IdP groups to FlowPilot roles:

```python
role_mapping = {
    'Engineering-Team': 'Member',
    'Engineering-Admins': 'Admin',
    'CTO': 'Owner'
}
```

## Security Considerations

### PKCE (Proof Key for Code Exchange)

PKCE is enabled by default for OAuth 2.0 flows to prevent authorization code interception attacks.

### Token Storage

- Access tokens and refresh tokens are encrypted using `django-cryptography`
- Tokens are never logged or exposed in API responses
- Sessions are tracked with secure random session IDs

### Audit Logging

All SSO events are logged with:
- Event type (login, logout, errors, etc.)
- Severity level (info, warning, error, critical)
- User information
- IP address and user agent
- Timestamp
- Error details (if applicable)

### Domain Restrictions

Restrict SSO access to specific email domains:

```python
allowed_domains = ['yourcompany.com', 'subsidiary.com']
```

### SSO Enforcement

Force users to use SSO (disable password login):

```python
enforce_sso = True
```

## Testing

### Test SSO Connection

```bash
POST /api/v1/sso/connections/{id}/test/
```

Returns a test login URL that can be used to verify the SSO configuration.

### Unit Tests

Run SSO tests:

```bash
python manage.py test apps.sso
```

## Monitoring

### Session Metrics

- Active sessions
- Session duration
- Login success/failure rates
- Unique users

### Audit Events

- `login_initiated` - SSO login started
- `login_success` - User logged in successfully
- `login_failure` - Login failed
- `logout` - User logged out
- `user_provisioned` - New user created via SSO
- `user_updated` - User info updated via SSO
- `token_issued` - Access token issued
- `token_refreshed` - Access token refreshed
- `authentication_error` - Authentication failed
- `configuration_error` - SSO configuration error

## Celery Tasks

### Cleanup Tasks

```python
# Clean up expired sessions (runs every hour)
cleanup_expired_sessions.delay()

# Clean up expired state tokens (runs every hour)
cleanup_expired_state_tokens.delay()
```

### Metadata Refresh

```python
# Refresh SAML IdP metadata
refresh_idp_metadata.delay(connection_id)
```

### User Sync

```python
# Sync user info from SSO provider
sync_user_from_sso.delay(user_id, connection_id)
```

## Troubleshooting

### Common Issues

**Invalid redirect URI**
- Ensure redirect URI in IdP matches exactly (including trailing slash)
- Check for HTTP vs HTTPS mismatch

**Invalid state parameter**
- State tokens expire after 10 minutes
- Ensure cookies are enabled
- Check for clock skew between servers

**SAML assertion validation failed**
- Verify IdP certificate is correct
- Check clock skew (SAML is time-sensitive)
- Ensure ACS URL matches IdP configuration

**User not provisioned**
- Check `auto_provision_users` is enabled
- Verify attribute mapping is correct
- Check domain restrictions

### Debug Mode

Enable detailed logging:

```python
LOGGING = {
    'loggers': {
        'apps.sso': {
            'level': 'DEBUG',
            'handlers': ['console'],
        }
    }
}
```

## Compliance

### SOC 2

- Comprehensive audit logging
- Session tracking with IP addresses
- Token encryption at rest
- Secure token transmission (HTTPS only)

### GDPR

- User data export capability
- User deletion support
- Audit trail for data access

### HIPAA

- Encrypted tokens and credentials
- Detailed access logs
- Session timeout enforcement

## API Examples

### Initiate SSO Login

```bash
curl -X POST https://api.flowpilot.ai/api/v1/sso/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "connection_id": "123e4567-e89b-12d3-a456-426614174000",
    "redirect_uri": "https://app.flowpilot.ai/sso/callback"
  }'
```

Response:
```json
{
  "authorization_url": "https://accounts.google.com/o/oauth2/v2/auth?client_id=...",
  "state": "random-state-parameter"
}
```

### Create SSO Connection

```bash
curl -X POST https://api.flowpilot.ai/api/v1/sso/connections/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "organization": "org-uuid",
    "provider": "provider-uuid",
    "name": "Google SSO",
    "client_id": "your-client-id",
    "client_secret": "your-client-secret",
    "redirect_uri": "https://app.flowpilot.ai/sso/callback",
    "auto_provision_users": true,
    "allowed_domains": ["yourcompany.com"]
  }'
```

## Support

For issues or questions:
- GitHub Issues: https://github.com/flowpilot-ai/flowpilot/issues
- Documentation: https://docs.flowpilot.ai/sso
- Email: support@flowpilot.ai
