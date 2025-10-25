# signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver

from notifications.models import Notification
from datetime import date
import uuid
from .models import SupervisorFormModel

@receiver(post_save, sender=SupervisorFormModel)
def send_supervisorform_notification(sender, instance, created, **kwargs):
    """
    Automatically send notification when a new supervisor form is submitted.
    """
    print("Signal triggered for SupervisorFormModel")
    if created:

        Notification.objects.create(
             # the supervisor receiving the form
            title="New Supervisor Form Submitted",
            for_admin=True,
            message=f"A new supervisor form has been submitted by {instance.supervisor.name} "
                    f"for {instance.employee.name} on {instance.report_date}.",
          #  notification_type='status'  # optional
        )

    