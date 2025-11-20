"""Django admin for Connectors app."""
from django.contrib import admin
from .models import Connector, ConnectorCredential, ConnectorWebhook, ConnectorSyncLog

@admin.register(Connector)
class ConnectorAdmin(admin.ModelAdmin):
    list_display = ['organization', 'provider', 'name', 'is_active', 'created_at']
    list_filter = ['provider', 'is_active']
    search_fields = ['name', 'organization__name']

@admin.register(ConnectorCredential)
class ConnectorCredentialAdmin(admin.ModelAdmin):
    list_display = ['connector', 'expires_at', 'created_at']

@admin.register(ConnectorWebhook)
class ConnectorWebhookAdmin(admin.ModelAdmin):
    list_display = ['connector', 'event_type', 'is_active', 'created_at']

@admin.register(ConnectorSyncLog)
class ConnectorSyncLogAdmin(admin.ModelAdmin):
    list_display = ['connector', 'operation', 'status', 'records_processed', 'created_at']
    list_filter = ['status', 'operation']
