"""Django admin for Billing app."""
from django.contrib import admin
from .models import BillingUsage, SubscriptionPlan, OrganizationSubscription, Invoice, APIKey

@admin.register(BillingUsage)
class BillingUsageAdmin(admin.ModelAdmin):
    list_display = ['organization', 'usage_type', 'quantity', 'total_cost', 'created_at']
    list_filter = ['usage_type', 'created_at']
    search_fields = ['organization__name']

@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ['name', 'tier', 'monthly_price', 'annual_price', 'is_active']
    list_filter = ['tier', 'is_active']

@admin.register(OrganizationSubscription)
class OrganizationSubscriptionAdmin(admin.ModelAdmin):
    list_display = ['organization', 'plan', 'status', 'billing_cycle', 'current_period_end']
    list_filter = ['status', 'billing_cycle']
    search_fields = ['organization__name']

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ['invoice_number', 'organization', 'status', 'total', 'due_date', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['invoice_number', 'organization__name']

@admin.register(APIKey)
class APIKeyAdmin(admin.ModelAdmin):
    list_display = ['name', 'prefix', 'organization', 'created_by', 'is_active', 'last_used_at', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'organization__name', 'created_by__email']
    readonly_fields = ['key', 'prefix', 'last_used_at', 'created_at', 'updated_at']

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'organization', 'created_by')
        }),
        ('Key Details', {
            'fields': ('key', 'prefix')
        }),
        ('Permissions & Security', {
            'fields': ('permissions', 'allowed_ips', 'is_active', 'expires_at')
        }),
        ('Usage', {
            'fields': ('last_used_at', 'metadata')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
