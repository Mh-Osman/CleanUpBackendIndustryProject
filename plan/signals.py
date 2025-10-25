#signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver

from notifications.models import Notification
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
        #notification 
        Notification.objects.create(
            for_user=instance.user,
            title="New Invoice Generated",
            message=f"An invoice {invoice.invoice_id} has been generated for your subscription to plan {instance.plan.name}.",
            for_all=False,
            for_admin=True,
        )

from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
# ----------------------------
# 2️⃣ Send notification when employees are added
# ----------------------------
@receiver(m2m_changed, sender=Subscription.employee.through)
def notify_employees_added(sender, instance, action, pk_set, **kwargs):
    if action == "post_add":  # after employees are added
        employees = instance.employee.filter(pk__in=pk_set)
        namesandusertype = ", ".join([f"{emp.name} ({emp.user_type})" for emp in employees])
        for emp in employees:
            Notification.objects.create(
                for_user=emp,
                title="New Subscription Assigned",
                
                message=f"You have been assigned to a new subscription for user {instance.user.name} "
                        f"under plan {instance.plan.name}. Employees assigned: {namesandusertype}",
                
                for_all=False,
                for_admin=True,
                
               
            )