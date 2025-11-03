from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import ClientCheckoutForm
from notifications.models import Notification

@receiver(post_save, sender=ClientCheckoutForm)
def create_client_checkout_form(sender, instance, created, **kwargs):
    print("Signal received for ClientCheckoutForm creation.")
    if not created:
        return
    
    print("ClientCheckoutForm created signal triggered.")
    client = instance.client
    print(f"Client: {client}")
    # Notify subscription employees
    if instance.subscription:
        for emp in instance.subscription.employee.all():
            message = f"New Client Checkout Form '{instance.form_name}' created by {client.name}."
            Notification.objects.create(
                title="New Client Checkout Form",
                for_user=emp,   # not emp_id
                message=message,
                for_admin=False,
                for_all=False
            )

    # Notify special service worker
    if instance.special_service:
        emp = instance.special_service.worker
        message = f"New Client Checkout Form '{instance.form_name}' created by {client.name}."
        Notification.objects.create(
            title="New Client Checkout Form",
            for_user=emp,
            message=message,
            for_admin=False,
            for_all=False
        )

    # Notify admin
    Notification.objects.create(
        title="New Client Checkout Form Created",
        message=f"A new Client Checkout Form '{instance.form_name}' has been created by {client.name}. Please review it.",
        for_admin=True,
        for_all=False
    )

    print("Notifications created for ClientCheckoutForm creation.")

    
