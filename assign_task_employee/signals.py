# services/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import SpecialServicesModel
from notifications.models import Notification  # import your Notification model

@receiver(post_save, sender=SpecialServicesModel)
def send_assignment_notification(sender, instance, created, **kwargs):
    """
    Automatically send notification when a new service/task is assigned to a worker.
    """
    print("Signal triggered for SpecialServicesModel")
    if created:

        Notification.objects.create(
            for_user=instance.worker,  # the employee receiving the task
            title="New Task Assigned ",
            message=f"You have been assigned a new task: {instance.name} "
                    f"at {instance.building.name}, {instance.region.name}.",
            for_admin=True,
          #  notification_type='status'  # optional
        )
