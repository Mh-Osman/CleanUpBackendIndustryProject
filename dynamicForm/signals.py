# subscriptions/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver

from notifications.models import Notification
from datetime import date
import uuid
from .models import FormSubmissionModel
@receiver(post_save, sender=FormSubmissionModel)
def send_form_submission_notification(sender, instance, created, **kwargs):
    """
    Automatically send notification when a new form submission is created.
    """
    if created:
        Notification.objects.create(
            for_user=instance.response_user.name,
            title="New Form Submission",
            for_admin=True,
            message=f"A new form has been submitted by {instance.response_user.name}.",
          #  notification_type='form_submission'
        )

from .models import FormNameModel
@receiver(post_save, sender=FormNameModel)
def send_formname_creation_notification(sender, instance, created, **kwargs):
    """
    Automatically send notification when a new form name is created.
    """
    if created:
        Notification.objects.create(
            for_admin=True,
            title="New Form Name Created",
            message=f"A new form name '{instance.form_name}' has been created.",
            for_all=True,
          #  notification_type='form_name_creation'
        )