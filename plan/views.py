from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from .models import PlanModel, Subscription,SubscriptionHistory,InvoiceModel,InvoiceLineItem
import stripe
from django.conf import settings
from locations.models import Apartment, Building,Region
from datetime import datetime, timedelta
import stripe
from django.utils import timezone
from .serializers import PlanSerailzier,SubscribeSerializerDetails,SubscriptionStatusCountSerializer,InvoiceLineItemSerializer,InvoiceSerializer,CalculationsForInvoice,SubscriptionCreateSerializer
from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics
from django.db.models import Sum

# stripe.api_key = settings.STRIPE_SECRET_KEY


class PlanView(viewsets.ModelViewSet):
    queryset=PlanModel.objects.all().order_by('-created_at')
    serializer_class=PlanSerailzier
    # permission_classes=[permissions.AllowAny]
    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]
 
        
    
  
          
class SubscriptionListCreateView(viewsets.ModelViewSet):
    queryset = Subscription.objects.all().order_by('-created_at')
    serializer_class = SubscriptionCreateSerializer
    permission_classes = [permissions.IsAdminUser]

    def perform_create(self, serializer):
        sub=serializer.save()
        SubscriptionHistory.objects.create(
              subscription=sub,
              amount=sub.plan.amount,
              action="active",
              start_date=sub.start_date,
              end_date=sub.current_period_end
              )



class CustomPermissionForSubscriptionEmployeeAndAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return [permissions.IsAuthenticated]
        
    def has_object_permission(self, request, view, obj):
        return [permissions.IsAdminUser]


class SubscriptionSerializerView(generics.ListAPIView):
    # permission_classes = [permissions.IsAuthenticated]
    permission_classes = [CustomPermissionForSubscriptionEmployeeAndAdmin]
    # permission_classes = [permissions.AllowAny]
    queryset=Subscription.objects.all().order_by("-created_at")
    serializer_class=SubscribeSerializerDetails
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'plan', 'user', 'building', 'region', 'apartment']
    def get_queryset(self):
        if not self.request.user.is_staff:
            return self.queryset.filter(
                Q(user=self.request.user) | Q(employee=self.request.user)
            )
        return self.queryset
    

# full subscription view
class SubcriptionFullStatusDetailView(APIView):
    permission_classes=[permissions.IsAdminUser]

    def get(self,request):
        now=timezone.now()
        one_month_ago = now - timedelta(days=30)
        data={
            'active':Subscription.objects.filter(status='active').count(),
            'pending':Subscription.objects.filter(status='past_due').count(), # its means auto renewal need
            'expired':Subscription.objects.filter(status='canceled').count(),
            'inactive':Subscription.objects.filter(status='inactive').count(),
            'total_revinew_last_month':SubscriptionHistory.objects.filter(created_at__gte=one_month_ago,action='active').aggregate(total=Sum('amount'))['total'] or 0

        }
        serializer=SubscriptionStatusCountSerializer(data)
        return Response(serializer.data)
    
    
     
              
        

# class CreateCheckoutSession(APIView):
#     permission_classes = [permissions.IsAuthenticated]

#     def post(self, request):
#         plan_id = request.data.get("plan_id")
#         building_id = request.data.get("building_id")
#         apartment_id = request.data.get("apartment_id")
#         region_id=request.data.get('region_id')
#         user = request.user

        
#         try: plan = PlanModel.objects.get(id=plan_id)
#         except PlanModel.DoesNotExist: return Response({"error":"plan not found"}, status=404)
#         try: building = Building.objects.get(id=building_id)
#         except Building.DoesNotExist: return Response({"error":"Building not found"}, status=404)
#         try: apartment = Apartment.objects.get(id=apartment_id)
#         except Apartment.DoesNotExist: return Response({"error":"Apartment not found"}, status=404)
#         try:region=Region.objects.get(id=region_id)
#         except Region.DoesNotExist: return Response({"error":"Region not found"},status=404)

        
#         subscription = Subscription.objects.filter(user=user, plan=plan, building=building,region=region,apartment=apartment,status__in=['active','paused','past_due']).first()
#         if subscription :
#             if subscription.status=='active':
#                 return Response("You already have this paln on this apartment ! kindly contact with Us !")
#             if subscription.status=='paused':
#                 return Response("You Have this plan but it's temporary paused ,contract with admin ")
#             if subscription.status=='past_due':
#                 return Response("Recharge your account and contact with admin")
            
#         subscription = Subscription.objects.filter(user=user, plan=plan, building=building,region=region,apartment=apartment,status='inactive').first()
    
#         if subscription and subscription.stripe_customer_id:
#             customer_id = subscription.stripe_customer_id
#         else:
#             customer = stripe.Customer.create(email=user.email)
#             customer_id = customer.id
        
 
#         session = stripe.checkout.Session.create(
#             customer=customer_id,
#             payment_method_types=["card"],
#             line_items=[
#                 {"price": plan.stripe_price_id, 
#                  "quantity": 1}
#                 ],
#             mode="subscription",
#             success_url="http://localhost:3000/success",
#             cancel_url="http://localhost:3000/cancel"
#         )


#         if not subscription:
#             subscription = Subscription.objects.create(
#                 user=user,
#                 plan=plan,
#                 stripe_customer_id=customer_id,
#                 status="inactive",
#                 building=building,
#                 apartment=apartment,
#                 region=region
#             )
#         else:
#             subscription.stripe_customer_id = customer_id
#             subscription.save()

#         return Response({"checkout_url": session.url})


class PauseSubscription(APIView):
    permission_classes = [permissions.IsAdminUser]

    def post(self, request, subscription_id):
        try:
            sub = Subscription.objects.get(id=subscription_id)
        except Subscription.DoesNotExist:
            return Response({"error":"Subscription not found"}, status=404)

        # if not sub.stripe_subscription_id:
        #     return Response({"error":"No Stripe subscription ID"}, status=400)

        if sub.status!="active":
            return Response({"error":"first active your sub'scription then try to pause"})
    
        # try:
        #   stripe.Subscription.modify(
        #     sub.stripe_subscription_id,
        #     pause_collection={
        #         "behavior": "keep_as_draft",
        #         "resumes_at": int((datetime.now() + timedelta(days=30)).timestamp())  # example 30 days
        #     }
        #  )
        # except stripe.error.InvalidRequestError as e:
        #   return Response({"error": f"Stripe error: {str(e)}"}, status=400)
       
        sub.status = "paused"
        sub.pause_until = datetime.now() + timedelta(days=30)
        sub.paused_at=timezone.now().date()
        sub.save()
        SubscriptionHistory.objects.create(
              subscription=sub,
              amount=sub.plan.amount,
              action="paused",
              start_date=sub.start_date,
              end_date=sub.current_period_end
              )

        return Response({"message":"Subscription paused successfully !"})



class ResumeSubscription(APIView):
    permission_classes = [permissions.IsAdminUser]

    def post(self, request, subscription_id):
        
        try:
            sub = Subscription.objects.get(id=subscription_id)
            print(sub)
        except Subscription.DoesNotExist:
            return Response({"error":"Subscription not found"}, status=404)
        
        # if not sub.stripe_subscription_id:
        #     return Response({"error":"No Stripe subscription ID"}, status=400)

        if sub.status!="paused":
            return Response({"error":"first paused your sub'scription"})
        # try:
        #     stripe_sub=stripe.Subscription.modify(
        #     sub.stripe_subscription_id,
        #     pause_collection=None
        # )
        #     print(stripe_sub)
        # except stripe.error.InvalidRequestError as e:
        #   return Response({"error": f"Stripe error: {str(e)}"}, status=400)
    
        sub.status = "active"  
        sub.pause_until = None 
        sub.paused_at=None
        sub.save()
        SubscriptionHistory.objects.create(
              subscription=sub,
              amount=sub.plan.amount,
              action="resumed",
              start_date=sub.start_date,
              end_date=sub.current_period_end
              )
       
        return Response({"message":"Resumed Successfully !"})


class StopSubscription(APIView):
    permission_classes = [permissions.IsAdminUser]

    def post(self, request, subscription_id):
        try:
            sub = Subscription.objects.get(id=subscription_id)
        except Subscription.DoesNotExist:
            return Response({"error":"Subscription not found"}, status=404)
        
        # if not sub.stripe_subscription_id:
        #     return Response({"error":"No Stripe subscription ID"}, status=400)
        # try:
        #   stripe.Subscription.delete(sub.stripe_subscription_id)
        # except stripe.error.InvalidRequestError as e:
        #   return Response({"error": f"Stripe error: {str(e)}"}, status=400)

        sub.status="canceled"
        sub.canceled_at=timezone.now().date()
        sub.save()
        SubscriptionHistory.objects.create(
              subscription=sub,
              amount=sub.plan.amount,
              action="cancel",
              start_date=sub.start_date,
              end_date=sub.current_period_end
              )
       
        return Response({"message":"Subscription Stoped Successfully !"})





# invoice 

   
    
class InvoiceView(viewsets.ModelViewSet):
    queryset=InvoiceModel.objects.all().order_by('-created_at')
    serializer_class=InvoiceSerializer
    def get_permissions(self):
        request=self.request.method
        if self.request.method in permissions.SAFE_METHODS:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAdminUser()]

    def get_queryset(self):
        user=self.request.user
        if not user.is_staff:
            return  self.queryset.filter(Q(client=user) | Q(vendor=user))
        return self.queryset

from  django.db.models import Q

class CalculationsForInvoiceView(APIView):
        permission_classes=[permissions.IsAdminUser]
        def get(self, request, *args, **kwargs):
            total=InvoiceModel.objects.aggregate(total=Sum('total_amount'))['total'] or 0
            expense=InvoiceModel.objects.filter(Q(vendor__isnull=False),Q(client__isnull=True)).aggregate(expense=Sum('total_amount'))['expense'] or 0
            sales=InvoiceModel.objects.filter(Q(client__isnull=False),Q(vendor__isnull=True)).aggregate(expense=Sum('total_amount'))['expense'] or 0
            total_invoice=InvoiceModel.objects.all().count()
            paid=InvoiceModel.objects.filter(status='paid').count()
            unpaid=InvoiceModel.objects.filter(status='unpaid').count()
            return Response({
            "total":total,
            "sales":sales,
            "expense":expense,
            "total_invoice":total_invoice,
            "paid":paid,
            "unpaid":unpaid,
        })