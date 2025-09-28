from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.conf import settings
from .models import Subscription
from django.contrib.auth import get_user_model
from django.utils import timezone
# from datetime import datetime
from datetime import datetime, timezone as dt_timezone
from django.utils.timezone import make_aware
import stripe
import json

User = get_user_model()
stripe.api_key = settings.STRIPE_SECRET_KEY

# webhooks.py
# webhooks.py

from .models import Subscription

stripe.api_key = settings.STRIPE_SECRET_KEY

@csrf_exempt
def stripe_webhook(request):
    payload = request.body.decode('utf-8')
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE", "")
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except Exception:
        return HttpResponse(status=400)

    obj = event['data']['object']

    
    if event['type'] in ['checkout.session.completed','invoice.payment_succeeded']:
        customer_id = obj.get("customer")
        subscription_id = subscription_id_parent = obj.get('parent', {}) \
                                .get('subscription_details', {}) \
                                .get('subscription')
        
        sub = Subscription.objects.filter(stripe_customer_id=customer_id).first()

        if sub:
          sub.status = "active"

          if subscription_id:
            sub.stripe_subscription_id = subscription_id
            stripe_sub = stripe.Subscription.retrieve(subscription_id)
            # if event['type'] == 'invoice.payment_succeeded':
            #     print("Success: ")

            line_item = obj['lines']['data'][0]

            period_start_ts = line_item['period']['start']
            period_end_ts   = line_item['period']['end']

            period_start = datetime.fromtimestamp(period_start_ts, tz=dt_timezone.utc)
            period_end   = datetime.fromtimestamp(period_end_ts, tz=dt_timezone.utc)

            if period_start:
                sub.start_date = period_start
            if period_end:
                sub.current_period_end = period_end
            sub.save()
       
            
    
   
    elif event['type'] == 'invoice.payment_failed':
        customer_id = obj.get("customer")
        sub = Subscription.objects.filter(stripe_customer_id=customer_id).first()
        if sub:
            sub.status = "past_due"
            sub.save()

   
    elif event['type'] == 'customer.subscription.deleted':
        stripe_sub_id = obj.get("id")
        sub = Subscription.objects.filter(stripe_subscription_id=stripe_sub_id).first()
        if sub:
            sub.status = "canceled"
            sub.save()


    elif event['type'] == 'customer.subscription.updated':
        print("hello i am updated")
        stripe_sub_id = obj.get("id")
        sub = Subscription.objects.filter(stripe_subscription_id=stripe_sub_id).first()
        if sub:
          
            pause_collection = obj.get("pause_collection")
            if pause_collection:
                sub.status = "paused"
                resumes_at_ts = pause_collection.get("resumes_at")
                if resumes_at_ts:
                    sub.pause_until = timezone.datetime.fromtimestamp(resumes_at_ts, tz=dt_timezone.utc)
            else:
                
                sub.status = "active"
                sub.pause_until = None
                period_end   = datetime.fromtimestamp(period_end_ts, tz=dt_timezone.utc)
                if period_end:
                 sub.current_period_end = period_end

            
            
            sub.save()
    # elif event['type'] == 'customer.subscription.updated':
    # stripe_sub_id = obj.get("id")
    # sub = Subscription.objects.filter(stripe_subscription_id=stripe_sub_id).first()
    # if sub:

    #     # Pause/resume handling
    #     pause_collection = obj.get("pause_collection")
    #     if pause_collection:
    #         sub.status = "paused"
    #         resumes_at_ts = pause_collection.get("resumes_at")
    #         if resumes_at_ts:
    #             sub.pause_until = timezone.datetime.fromtimestamp(resumes_at_ts, tz=dt_timezone.utc)
    #     else:
    #         sub.status = "active"
    #         sub.pause_until = None

    #     # Update subscription period
    #     period_start_ts = obj.get("current_period_start")
    #     period_end_ts   = obj.get("current_period_end")

    #     if period_start_ts:
    #         sub.start_date = timezone.datetime.fromtimestamp(period_start_ts, tz=dt_timezone.utc)
    #     if period_end_ts:
    #         sub.current_period_end = timezone.datetime.fromtimestamp(period_end_ts, tz=dt_timezone.utc)

    #     sub.save()


    return HttpResponse(status=200)




