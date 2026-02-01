from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from .models import Notification

@shared_task(bind=True, autoretry_for=(Exception,), retry_kwargs={'max_retries': 3, 'countdown': 10})
def delete_old_notifications(self, days=30):
    cutoff_date = timezone.now() - timedelta(days=days)

    deleted_count, _ = Notification.objects.filter(
        created_at__lt=cutoff_date
    ).delete()

    return f"{deleted_count} notifications deleted"
