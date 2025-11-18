#signals.py

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from notifications.models import Notification
from .models import Subscription,InvoiceModel 
from datetime import date,timedelta
import uuid



@receiver(pre_save, sender=Subscription)
def generate_invoice_on_active(sender, instance, **kwargs):
    if not instance.pk:
        # new subscription, ignore
        return
    previous = Subscription.objects.get(pk=instance.pk)
    if previous.status == 'past_due' and instance.status == 'active':
        invoice_id = f"INV-{uuid.uuid4().hex[:8].upper()}"
        # instance.current_period_end=instance.start_date+timedelta(days=30)
        # instance.save()
        invoice_status_value = "paid" if instance.status == "active" else "unpaid"

        invoice = InvoiceModel.objects.create(
            invoice_id=invoice_id,
            type="outgoing",  
            date_issued=date.today(),
            due_date=instance.current_period_end,  
            status=invoice_status_value, 
            building=instance.building,
            client=instance.user,
            plan=instance.plan,
            total_amount=instance.plan.amount,
            note=f"Subscription created for {instance.user.email}",
        )


@receiver(post_save, sender=Subscription)
def create_invoice_for_subscription(sender, instance, created, **kwargs):
    invoice_status_value = "paid" if instance.status == "active" else "unpaid"
    if created:
    
        invoice_id = f"INV-{uuid.uuid4().hex[:8].upper()}"
        instance.current_period_end=instance.start_date+timedelta(days=30)
        instance.save()

       
        invoice = InvoiceModel.objects.create(
            invoice_id=invoice_id,
            type="outgoing",  
            date_issued=date.today(),
            due_date=instance.current_period_end,  
            status=invoice_status_value, 
            building=instance.building,
            client=instance.user,
            plan=instance.plan,
            total_amount=instance.plan.amount,
            note=f"Subscription created for {instance.user.email}",
        )



# =======
#         # invoice=InvoiceModel.objects.create(
#         #     invoice_id=str(uuid.uuid4()),  # unique invoice ID
#         #     type="outgoing",
#         #     date_issued=subscription.start_date,
#         #     due_date=subscription.current_period_end,
#         #     client=subscription.user,
#         #     plan=subscription.plan,
#         #     note=f"{self.request.user.name} subscribed",
#         #     status="paid" if getattr(subscription, "payment_method", "prepaid") == "prepaid" else "unpaid",
#         #     total_amount=subscription.plan.amount,
#         #     building=subscription.building
#         # )
# >>>>>>> origin/testingallmerge
#         # If the subscription has an apartment, add it
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