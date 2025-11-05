#signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver

from notifications.models import Notification
from .models import Subscription,InvoiceModel # import your Invoice model
from datetime import date,timedelta
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
        instance.current_period_end=instance.start_date+timedelta(days=30)
        instance.save()

        # Create the invoice
        invoice = InvoiceModel.objects.create(
            invoice_id=invoice_id,
            type="outgoing",  # since it's a sale to a client
            date_issued=date.today(),
            due_date=date.today(),  # or add 7 days etc.
            status="paid" if getattr(instance, "payment_method", "prepaid") == "prepaid" else "unpaid" , # or any default status you use
            building=instance.building,
            client=instance.user,
            plan=instance.plan,
            total_amount=instance.plan.amount,
            note=f"Subscription created for {instance.user.email}",
        )
# <<<<<<< HEAD


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

    #osman added this for apartment 
    # 
    if instance.apartment:
        apartment_obj = instance.apartment
        apartment_obj.client = instance.user
        apartment_obj.building = instance.building
        apartment_obj.region = instance.region

        region_obj = instance.region
        region_name = region_obj.name if region_obj else "No Region"
        region_str = str(region_obj.id) if region_obj else "0"
        client_id = str(instance.user.id)

        if len(region_str) == 1:
            r = "00" + region_str
        elif len(region_str) == 2:
            r = "0" + region_str
        else:
            r = region_str

        if len(client_id) == 1:
            c = "00" + client_id
        elif len(client_id) == 2:
            c = "0" + client_id
        else:
            c = client_id

        apartment_obj.apartment_code = r+"-"+c
        apartment_obj.apartment_code2 = region_name+"-"+c
        apartment_obj.save() 

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