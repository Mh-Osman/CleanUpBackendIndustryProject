from django.shortcuts import render
from locations.models import Building
from plan.models import Subscription,InvoiceModel
from django.contrib.auth  import get_user_model
from rest_framework.views import APIView
from datetime import datetime
from rest_framework.response import Response
from .serializers import  DashBoardTopSerializer
from django.db.models import Sum
User=get_user_model()
import calendar
# Create your views here.

class DashBoardTopView(APIView):
  def post(self, request, *args, **kwargs):
      serializer=DashBoardTopSerializer(data=request.data)
      if serializer.is_valid(raise_exception=True):
         print(serializer.data)
         month=serializer.validated_data.get('month')
         year=serializer.validated_data.get('year')
         clients=User.objects.filter(
            user_type="employee",
            date_joined__month=month,
            date_joined__year=year
         ).count()

         new_subscription=Subscription.objects.filter(
            created_at__month=month,
            created_at__year=year,
         ).count()

         #total i revenue from invoice
        
         month_total_revenue=InvoiceModel.objects.filter(
            created_at__month=month,
            created_at__year=year,
            type='outgoing'
         ).aggregate(total=Sum('sub_total'))['total'] or 0


         total_building=Building.objects.filter(
            created_at__month=month,
            created_at__year=year
         ).count()

         analitycs={
            
            "stopped":Subscription.objects.filter(
               canceled_at__month=month,
               canceled_at__year=year,
            ).count(),
            "paused":Subscription.objects.filter(
               paused_at__month=month,
               paused_at__year=year
            ).count()
            
         }

         outgoing_sales = InvoiceModel.objects.filter(
                created_at__month=month,
                created_at__year=year,
                type='outgoing'
            ).values(
                'created_at', 'sub_total'
            ).order_by('-created_at')

        # Format each sale record
         formatted_sales = []
         for sale in outgoing_sales:
                created_time = sale['created_at']
                formatted_sales.append({
                    "time": created_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "amount": float(sale['sub_total']),
                    "month": calendar.month_name[created_time.month]
                })
         return Response(
            {
               'clients':clients,
               'month_new_subscription':new_subscription,
               'month_revenue_from_invoice':month_total_revenue,
               'month_new_added_building':total_building,
               'analitycs':analitycs,
               'outgoing_sales': formatted_sales
            }
         )
         
         


         
         


      
      



        