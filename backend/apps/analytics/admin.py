"""Django admin for Analytics app."""
from django.contrib import admin
from .models import DailyMetrics, UserActivity, ErrorLog

@admin.register(DailyMetrics)
class DailyMetricsAdmin(admin.ModelAdmin):
    list_display = ['organization', 'date', 'total_executions', 'total_ai_tokens', 'total_ai_cost']
    list_filter = ['date']
    search_fields = ['organization__name']

@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    list_display = ['user_email', 'action', 'organization', 'created_at']
    list_filter = ['action', 'created_at']
    search_fields = ['user_email', 'resource_id']

@admin.register(ErrorLog)
class ErrorLogAdmin(admin.ModelAdmin):
    list_display = ['error_type', 'severity', 'count', 'is_resolved', 'last_seen']
    list_filter = ['severity', 'is_resolved', 'last_seen']
    search_fields = ['error_type', 'error_message']
