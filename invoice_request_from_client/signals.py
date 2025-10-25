from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import InvoiceRequestFromEmployee
from plan.models import InvoiceModel
import uuid
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver

@receiver(pre_save, sender=InvoiceRequestFromEmployee)
def store_previous_status(sender, instance, **kwargs):
    if instance.pk:
        previous = sender.objects.get(pk=instance.pk)
        instance._previous_status = previous.status
    else:
        instance._previous_status = None

@receiver(post_save, sender=InvoiceRequestFromEmployee)
def create_invoice_on_approval(sender, instance, created, **kwargs):
    if not created:

        if (getattr(instance, "_previous_status", None) != "Approved" and instance.status == "Approved") or (getattr(instance, "_previous_status", None) != "Cancel" and instance.status == "Approved"):
            invoice = InvoiceModel.objects.create(
                vendor=instance.vendor,
                date_issued=instance.expense_date,
                invoice_id=f"INV-{uuid.uuid4().hex[:8].upper()}",
                vendor_name=instance.vendor_name,
                type="incoming",
                vendor_invoice_file=instance.receipt,
                note=instance.discription,
                total_amount=instance.amount,
                status="paid",
            )
            if invoice:
                invoice.expense_category.set(instance.expense_category.all())





