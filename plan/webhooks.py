from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.conf import settings
from .models import Subscription,InvoiceModel
from django.contrib.auth import get_user_model
from django.utils import timezone
# from datetime import datetime
from datetime import datetime, timezone as dt_timezone
from django.utils.timezone import make_aware
import stripe
from rest_framework.response import Response
import json

User = get_user_model()
stripe.api_key = settings.STRIPE_SECRET_KEY


from .models import Subscription,SubscriptionHistory

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

    
    if event['type'] in 'invoice.payment_succeeded':
        customer_id = obj.get("customer")
        subscription_id = obj.get('parent', {}) \
                                .get('subscription_details', {}) \
                                .get('subscription')
        
        sub = Subscription.objects.filter(stripe_customer_id=customer_id).first()

        if sub:
          sub.status = "active"


          if subscription_id:
            sub.stripe_subscription_id = subscription_id
            stripe_sub = stripe.Subscription.retrieve(subscription_id)

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
            SubscriptionHistory.objects.create(
              subscription=sub,
              amount=sub.plan.amount,
              action="active",
              start_date=sub.start_date,
              end_date=sub.current_period_end)
            invoice = InvoiceModel.objects.create(
                invoice_id=obj["id"],
                type="outgoing",
                date_issued=sub.start_date.date(),
                due_date=sub.current_period_end.date(),
                client=sub.user,
                plan=sub.plan,
                note=f"Stripe invoice {obj['id']}",
                status="paid",
                total_amount=sub.plan.amount,
                building=sub.building,
               
                )
            invoice.apartments.set([sub.apartment])
        
        
       
            
    
   
    elif event['type'] == 'invoice.payment_failed':
        customer_id = obj.get("customer")
        if not customer_id:
          return Response({"error": "No customer in webhook"}, status=400)
        sub = Subscription.objects.filter(stripe_customer_id=customer_id).first()
        if sub:
            sub.status = "past_due"
            sub.save()
            SubscriptionHistory.objects.create(
              subscription=sub,
              amount=sub.plan.amount,
              action="past_due",
              start_date=sub.start_date,
              end_date=sub.current_period_end
              )
            

   
    elif event['type'] == 'customer.subscription.deleted':
        stripe_sub_id = obj.get("id")
        sub = Subscription.objects.filter(stripe_subscription_id=stripe_sub_id).first()
        if sub:
            sub.status = "canceled"
            sub.save()
            SubscriptionHistory.objects.create(
              subscription=sub,
              amount=sub.plan.amount,
              action="cancelled",
              start_date=sub.start_date,
              end_date=sub.current_period_end
              )


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
                sub.save()
                SubscriptionHistory.objects.create(
              subscription=sub,
              amount=sub.plan.amount,
              action="paused",
              start_date=sub.start_date,
              end_date=sub.current_period_end
              )

            else:
                
                sub.status = "active"
                sub.pause_until = None
                
                
            
            sub.save()


    return HttpResponse(status=200)




