from celery import shared_task
from django.utils import timezone
from plan.models import Subscription

@shared_task
def auto_cancel_expired_subscriptions():
    today = timezone.now().date()
    print("i am running")

    # Only cancel subscriptions whose end date has passed and are not already canceled
    expired_subs = Subscription.objects.filter(current_period_end__lt=today,status='active')
    count = expired_subs.update(status='past_due')
    # count = expired_subs.update(satus='past_due')
    return f"{count} subscriptions automatically past_due."

