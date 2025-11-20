"""Django admin for Billing app."""
from django.contrib import admin
from .models import BillingUsage, SubscriptionPlan, OrganizationSubscription, Invoice

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
