from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.conf import settings
from .models import Subscription
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import datetime
from datetime import timezone as dt_timezone
import stripe

User = get_user_model()
stripe.api_key = settings.STRIPE_SECRET_KEY

# webhooks.py
# webhooks.py
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.conf import settings
from django.utils import timezone
import stripe

from .models import Subscription

stripe.api_key = settings.STRIPE_SECRET_KEY

@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE", "")
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except Exception:
        return HttpResponse(status=400)

    obj = event['data']['object']

    # 1️⃣ Payment succeeded
    if event['type'] in ['checkout.session.completed', 'invoice.payment_succeeded']:
        customer_id = obj.get("customer")
        subscription_id = obj.get("subscription")

        sub = Subscription.objects.filter(stripe_customer_id=customer_id).first()
        if sub:
            sub.status = "active"
            if subscription_id:
                sub.stripe_subscription_id = subscription_id
                stripe_sub = stripe.Subscription.retrieve(subscription_id)
                current_period_end_ts = stripe_sub.get("current_period_end")
                if current_period_end_ts:
                    sub.current_period_end = timezone.datetime.fromtimestamp(
                        current_period_end_ts, tz=dt_timezone.utc
                    )
            sub.save()

    # 2️⃣ Payment failed
    elif event['type'] == 'invoice.payment_failed':
        customer_id = obj.get("customer")
        sub = Subscription.objects.filter(stripe_customer_id=customer_id).first()
        if sub:
            sub.status = "past_due"
            sub.save()

    # 3️⃣ Subscription canceled
    elif event['type'] == 'customer.subscription.deleted':
        stripe_sub_id = obj.get("id")
        sub = Subscription.objects.filter(stripe_subscription_id=stripe_sub_id).first()
        if sub:
            sub.status = "canceled"
            sub.save()

    # 4️⃣ Subscription updated (handles pause/resume)
    elif event['type'] == 'customer.subscription.updated':
        stripe_sub_id = obj.get("id")
        sub = Subscription.objects.filter(stripe_subscription_id=stripe_sub_id).first()
        if sub:
            # Handle paused subscriptions
            pause_collection = obj.get("pause_collection")
            if pause_collection:
                sub.status = "paused"
                resumes_at_ts = pause_collection.get("resumes_at")
                if resumes_at_ts:
                    sub.pause_until = timezone.datetime.fromtimestamp(resumes_at_ts, tz=dt_timezone.utc)
            else:
                # If not paused, ensure active
                sub.status = "active"
                sub.pause_until = None

            # Update current_period_end
            current_period_end_ts = obj.get("current_period_end")
            if current_period_end_ts:
                sub.current_period_end = timezone.datetime.fromtimestamp(current_period_end_ts, tz=dt_timezone.utc)
            
            sub.save()

    return HttpResponse(status=200)




