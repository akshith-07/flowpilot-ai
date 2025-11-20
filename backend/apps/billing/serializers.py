"""
Serializers for Billing app.
"""
from rest_framework import serializers
from .models import BillingUsage, SubscriptionPlan, OrganizationSubscription, Invoice, APIKey


class SubscriptionPlanSerializer(serializers.ModelSerializer):
    """Serializer for SubscriptionPlan model."""

    class Meta:
        model = SubscriptionPlan
        fields = [
            'id', 'name', 'tier', 'description', 'monthly_price',
            'annual_price', 'max_workflows', 'max_executions_per_month',
            'max_ai_tokens_per_month', 'max_storage_gb', 'max_members',
            'features', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class OrganizationSubscriptionSerializer(serializers.ModelSerializer):
    """Serializer for OrganizationSubscription model."""

    plan_details = SubscriptionPlanSerializer(source='plan', read_only=True)
    organization_name = serializers.CharField(source='organization.name', read_only=True)

    class Meta:
        model = OrganizationSubscription
        fields = [
            'id', 'organization', 'organization_name', 'plan',
            'plan_details', 'status', 'billing_cycle',
            'current_period_start', 'current_period_end',
            'trial_end_date', 'stripe_customer_id',
            'stripe_subscription_id', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'stripe_customer_id', 'stripe_subscription_id',
            'created_at', 'updated_at'
        ]


class BillingUsageSerializer(serializers.ModelSerializer):
    """Serializer for BillingUsage model."""

    class Meta:
        model = BillingUsage
        fields = [
            'id', 'organization', 'usage_type', 'quantity',
            'unit_cost', 'total_cost', 'resource_id', 'metadata',
            'billing_period_start', 'billing_period_end', 'created_at'
        ]
        read_only_fields = ['id', 'total_cost', 'created_at']


class InvoiceSerializer(serializers.ModelSerializer):
    """Serializer for Invoice model."""

    organization_name = serializers.CharField(source='organization.name', read_only=True)

    class Meta:
        model = Invoice
        fields = [
            'id', 'organization', 'organization_name', 'invoice_number',
            'status', 'subtotal', 'tax', 'total', 'period_start',
            'period_end', 'stripe_invoice_id', 'paid_at', 'due_date',
            'line_items', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'invoice_number', 'stripe_invoice_id',
            'created_at', 'updated_at'
        ]


class APIKeySerializer(serializers.ModelSerializer):
    """Serializer for APIKey model."""

    organization_name = serializers.CharField(source='organization.name', read_only=True)
    created_by_email = serializers.EmailField(source='created_by.email', read_only=True)

    class Meta:
        model = APIKey
        fields = [
            'id', 'organization', 'organization_name', 'created_by',
            'created_by_email', 'name', 'prefix', 'description',
            'permissions', 'allowed_ips', 'is_active', 'expires_at',
            'last_used_at', 'metadata', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'prefix', 'last_used_at', 'created_at', 'updated_at'
        ]

    def to_representation(self, instance):
        """Hide full API key in normal responses."""
        data = super().to_representation(instance)
        # Only show prefix, not full key
        data.pop('key', None)
        return data


class APIKeyCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating API key (includes full key in response)."""

    class Meta:
        model = APIKey
        fields = ['name', 'description', 'permissions', 'allowed_ips', 'expires_at']

    def create(self, validated_data):
        """Create API key with organization and user context."""
        organization = self.context['request'].organization
        user = self.context['request'].user

        validated_data['organization'] = organization
        validated_data['created_by'] = user

        return super().create(validated_data)

    def to_representation(self, instance):
        """Include full API key in creation response."""
        data = super().to_representation(instance)
        data['id'] = str(instance.id)
        data['key'] = instance.key  # Show full key only on creation
        data['prefix'] = instance.prefix
        return data
