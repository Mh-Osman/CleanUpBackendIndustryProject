# subscriptions/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Subscription,InvoiceModel # import your Invoice model
from datetime import date
import uuid
@receiver(post_save, sender=Subscription)
def create_invoice_for_subscription(sender, instance, created, **kwargs):
    """
    When a new Subscription is created, automatically generate an invoice.
    """
    invoice_status_value = "paid" if instance.status == "active" else "unpaid"
    if created:
        # Generate a unique invoice ID
        invoice_id = f"INV-{uuid.uuid4().hex[:8].upper()}"

        # Create the invoice
        invoice = InvoiceModel.objects.create(
            invoice_id=invoice_id,
            type="outgoing",  # since it's a sale to a client
            date_issued=date.today(),
            due_date=date.today(),  # or add 7 days etc.
            status=invoice_status_value,  # or any default status you use
            building=instance.building,
            client=instance.user,
            plan=instance.plan,
            total_amount=instance.plan.amount
        )

        # If the subscription has an apartment, add it
        if instance.apartment:
            invoice.apartments.add(instance.apartment)

        invoice.save()
