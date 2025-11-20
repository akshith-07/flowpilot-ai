"""
Celery tasks for Connectors app.
"""
from celery import shared_task
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def sync_connector(self, connector_id):
    """
    Sync data from connector.

    Args:
        connector_id: Connector ID
    """
    try:
        from .models import Connector, ConnectorSyncLog
        from .services import ConnectorService
        from django.utils import timezone

        connector = Connector.objects.get(id=connector_id)

        # Create sync log
        sync_log = ConnectorSyncLog.objects.create(
            connector=connector,
            sync_type='manual',
            status='running',
            started_at=timezone.now()
        )

        try:
            # Perform sync
            result = ConnectorService.sync_data(connector)

            # Update sync log
            sync_log.status = 'completed'
            sync_log.completed_at = timezone.now()
            sync_log.records_synced = result.get('records_synced', 0)
            sync_log.records_failed = result.get('records_failed', 0)
            sync_log.metadata = result.get('metadata', {})
            sync_log.save()

            # Update connector last sync time
            connector.last_sync_at = timezone.now()
            connector.save(update_fields=['last_sync_at'])

            logger.info(f'Connector sync completed for {connector.id}: {result}')
            return result

        except Exception as e:
            # Update sync log with error
            sync_log.status = 'failed'
            sync_log.completed_at = timezone.now()
            sync_log.error_message = str(e)
            sync_log.save()

            logger.error(f'Connector sync failed for {connector.id}: {str(e)}')
            raise

    except Exception as e:
        logger.error(f'Connector sync task failed: {str(e)}')
        raise self.retry(exc=e, countdown=60)
