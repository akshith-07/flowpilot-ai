"""
Celery tasks for SSO operations.
"""
from celery import shared_task
from django.utils import timezone
from datetime import timedelta


@shared_task(name='apps.sso.cleanup_expired_sessions')
def cleanup_expired_sessions():
    """
    Clean up expired SSO sessions.
    Runs periodically to mark expired sessions as inactive.
    """
    from .models import SSOSession

    # Mark expired sessions as inactive
    expired_count = SSOSession.objects.filter(
        is_active=True,
        expires_at__lt=timezone.now()
    ).update(is_active=False)

    return f'Marked {expired_count} expired SSO sessions as inactive'


@shared_task(name='apps.sso.cleanup_expired_state_tokens')
def cleanup_expired_state_tokens():
    """
    Clean up expired SSO state tokens.
    Removes expired or used state tokens older than 1 hour.
    """
    from .models import SSOStateToken

    cutoff_time = timezone.now() - timedelta(hours=1)

    deleted_count, _ = SSOStateToken.objects.filter(
        expires_at__lt=cutoff_time
    ).delete()

    return f'Deleted {deleted_count} expired SSO state tokens'


@shared_task(name='apps.sso.refresh_idp_metadata')
def refresh_idp_metadata(connection_id):
    """
    Refresh IdP metadata for SAML connection.

    Args:
        connection_id: UUID of SSOConnection
    """
    from .models import SSOConnection, SSOAuditLog
    import requests

    try:
        connection = SSOConnection.objects.get(id=connection_id)

        if connection.provider.provider_type != 'saml2':
            return 'Connection is not SAML 2.0'

        if not connection.idp_metadata_url:
            return 'No IdP metadata URL configured'

        # Fetch metadata
        response = requests.get(connection.idp_metadata_url, timeout=30)
        response.raise_for_status()

        # Update metadata
        connection.idp_metadata_xml = response.text
        connection.last_sync_at = timezone.now()
        connection.last_error = None
        connection.save()

        SSOAuditLog.log_event(
            event_type='connection_updated',
            message='IdP metadata refreshed successfully',
            connection=connection,
            organization=connection.organization,
            severity='info'
        )

        return f'IdP metadata refreshed for connection {connection.name}'

    except SSOConnection.DoesNotExist:
        return f'SSO connection {connection_id} not found'
    except Exception as e:
        # Log error
        if 'connection' in locals():
            connection.last_error = str(e)
            connection.save()

            SSOAuditLog.log_event(
                event_type='metadata_error',
                message=f'IdP metadata refresh failed: {str(e)}',
                connection=connection,
                organization=connection.organization,
                severity='error',
                error_code='METADATA_REFRESH_FAILED',
                error_details={'error': str(e)}
            )

        return f'Failed to refresh IdP metadata: {str(e)}'


@shared_task(name='apps.sso.generate_sso_usage_report')
def generate_sso_usage_report(organization_id, start_date, end_date):
    """
    Generate SSO usage report for an organization.

    Args:
        organization_id: UUID of organization
        start_date: Start date (ISO format)
        end_date: End date (ISO format)

    Returns:
        dict: Usage statistics
    """
    from .models import SSOAuditLog, SSOSession
    from django.db.models import Count

    # Parse dates
    from datetime import datetime
    start = datetime.fromisoformat(start_date)
    end = datetime.fromisoformat(end_date)

    # Get login statistics
    login_stats = SSOAuditLog.objects.filter(
        organization_id=organization_id,
        created_at__gte=start,
        created_at__lte=end,
        event_type__in=['login_success', 'login_failure']
    ).values('event_type').annotate(count=Count('id'))

    # Get unique users
    unique_users = SSOSession.objects.filter(
        connection__organization_id=organization_id,
        created_at__gte=start,
        created_at__lte=end
    ).values('user').distinct().count()

    # Get provider distribution
    provider_stats = SSOSession.objects.filter(
        connection__organization_id=organization_id,
        created_at__gte=start,
        created_at__lte=end
    ).values('connection__provider__display_name').annotate(count=Count('id'))

    return {
        'organization_id': organization_id,
        'period': {'start': start_date, 'end': end_date},
        'login_stats': list(login_stats),
        'unique_users': unique_users,
        'provider_stats': list(provider_stats)
    }


@shared_task(name='apps.sso.sync_user_from_sso')
def sync_user_from_sso(user_id, connection_id):
    """
    Sync user information from SSO provider.

    Args:
        user_id: UUID of user
        connection_id: UUID of SSOConnection
    """
    from .models import SSOConnection, SSOSession
    from .services import OAuth2Service, OIDCService, UserProvisioningService
    from apps.users.models import User

    try:
        user = User.objects.get(id=user_id)
        connection = SSOConnection.objects.select_related('provider').get(id=connection_id)

        # Get active session
        session = SSOSession.objects.filter(
            user=user,
            connection=connection,
            is_active=True
        ).first()

        if not session:
            return 'No active SSO session found'

        # Check if token is expired
        if session.is_token_expired():
            # Refresh token
            if connection.provider.provider_type == 'oidc':
                service = OIDCService(connection)
            else:
                service = OAuth2Service(connection)

            if session.refresh_token_encrypted:
                tokens = service.refresh_access_token(session.refresh_token_encrypted)
                session.access_token_encrypted = tokens.get('access_token')
                session.access_token_expires_at = timezone.now() + timedelta(
                    seconds=tokens.get('expires_in', 3600)
                )
                session.save()
            else:
                return 'No refresh token available'

        # Get updated user info
        if connection.provider.provider_type in ['oauth2', 'oidc']:
            if connection.provider.provider_type == 'oidc':
                service = OIDCService(connection)
            else:
                service = OAuth2Service(connection)

            user_info = service.get_user_info(session.access_token_encrypted)

            # Update user
            provisioning_service = UserProvisioningService(connection)
            provisioning_service._update_user_from_sso(user, user_info)

            return f'User {user.email} synced successfully'

        return 'SSO provider does not support user sync'

    except (User.DoesNotExist, SSOConnection.DoesNotExist):
        return 'User or connection not found'
    except Exception as e:
        return f'User sync failed: {str(e)}'
