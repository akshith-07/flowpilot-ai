"""
Celery tasks for Billing app.
"""
from celery import shared_task
from django.utils import timezone
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True)
def generate_monthly_invoices(self):
    """
    Generate monthly invoices for all organizations.
    Runs on the 1st of each month.
    """
    try:
        from .models import OrganizationSubscription, Invoice, BillingUsage
        from apps.organizations.models import Organization
        import calendar
        from decimal import Decimal

        # Get active subscriptions
        subscriptions = OrganizationSubscription.objects.filter(
            status='active'
        ).select_related('organization', 'plan')

        for subscription in subscriptions:
            try:
                # Calculate billing period
                now = timezone.now()
                last_month = now.replace(day=1) - timedelta(days=1)
                period_start = last_month.replace(day=1).date()
                period_end = last_month.date()

                # Check if invoice already exists
                if Invoice.objects.filter(
                    organization=subscription.organization,
                    period_start=period_start,
                    period_end=period_end
                ).exists():
                    continue

                # Calculate usage costs
                usage_records = BillingUsage.objects.filter(
                    organization=subscription.organization,
                    billing_period_start__gte=period_start,
                    billing_period_end__lte=period_end
                )

                # Build line items
                line_items = [
                    {
                        'description': f'{subscription.plan.name} Subscription',
                        'quantity': 1,
                        'unit_price': float(subscription.plan.monthly_price),
                        'total': float(subscription.plan.monthly_price)
                    }
                ]

                # Add usage-based charges
                usage_total = Decimal('0.00')
                for usage in usage_records:
                    usage_total += usage.total_cost
                    line_items.append({
                        'description': f'{usage.get_usage_type_display()} - {usage.quantity} units',
                        'quantity': usage.quantity,
                        'unit_price': float(usage.unit_cost),
                        'total': float(usage.total_cost)
                    })

                # Calculate totals
                subtotal = subscription.plan.monthly_price + usage_total
                tax = subtotal * Decimal('0.00')  # TODO: Calculate tax based on location
                total = subtotal + tax

                # Generate invoice number
                invoice_number = f'INV-{subscription.organization.id.hex[:8].upper()}-{now.year}{now.month:02d}'

                # Create invoice
                Invoice.objects.create(
                    organization=subscription.organization,
                    invoice_number=invoice_number,
                    status='pending',
                    subtotal=subtotal,
                    tax=tax,
                    total=total,
                    period_start=period_start,
                    period_end=period_end,
                    due_date=now.date() + timedelta(days=14),
                    line_items=line_items
                )

                logger.info(f'Invoice generated for {subscription.organization.name}: {invoice_number}')

            except Exception as e:
                logger.error(f'Failed to generate invoice for {subscription.organization.name}: {str(e)}')

    except Exception as e:
        logger.error(f'Failed to generate monthly invoices: {str(e)}')


@shared_task(bind=True)
def track_usage(self, organization_id, usage_type, quantity, resource_id=None):
    """
    Track billable usage for an organization.

    Args:
        organization_id: Organization ID
        usage_type: Type of usage
        quantity: Quantity used
        resource_id: Optional resource ID
    """
    try:
        from .models import BillingUsage
        from apps.organizations.models import Organization
        from decimal import Decimal
        import calendar

        organization = Organization.objects.get(id=organization_id)

        # Get current billing period
        now = timezone.now()
        period_start = now.replace(day=1).date()
        last_day = calendar.monthrange(now.year, now.month)[1]
        period_end = now.replace(day=last_day).date()

        # Unit costs (these would typically come from a pricing table)
        unit_costs = {
            'workflow_execution': Decimal('0.01'),
            'ai_tokens': Decimal('0.000002'),  # per token
            'api_call': Decimal('0.001'),
            'storage': Decimal('0.023'),  # per GB
            'document_processing': Decimal('0.05')
        }

        unit_cost = unit_costs.get(usage_type, Decimal('0.00'))

        # Create usage record
        BillingUsage.objects.create(
            organization=organization,
            usage_type=usage_type,
            quantity=quantity,
            unit_cost=unit_cost,
            resource_id=resource_id,
            billing_period_start=period_start,
            billing_period_end=period_end
        )

        logger.info(f'Usage tracked for {organization.name}: {usage_type} x {quantity}')

    except Exception as e:
        logger.error(f'Failed to track usage: {str(e)}')
