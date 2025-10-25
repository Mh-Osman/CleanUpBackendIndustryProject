from django.shortcuts import render
from users.models import CustomUser
from locations.models import Building
from plan.models import Subscription,InvoiceModel
from django.contrib.auth  import get_user_model
from rest_framework.views import APIView
from datetime import datetime
from rest_framework.response import Response
from .serializers import  AdminUserSerializer, DashBoardTopSerializer
from django.db.models import Sum
from auditlog.models import LogEntry
from all_history.serializers import HistoryTrackSerializer
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
            user_type="client",
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
         ).aggregate(total=Sum('total_amount'))['total'] or 0


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
            ).count(),
            "new_active":new_subscription
            
         }
         top_clients = list(
                 InvoiceModel.objects.filter(
                    created_at__month=month,
                    created_at__year=year,
                    type='outgoing'
                )
                .values('client__id', 'client__name', 'client__email')
                .annotate(total_sales=Sum('total_amount'))
                .order_by('-total_sales')[:10]
            )

         
         outgoing_sales = InvoiceModel.objects.filter(
                created_at__month=month,
                created_at__year=year,
                type='outgoing'
            ).values(
                'created_at', 'total_amount'
            ).order_by('-created_at')
         
           

        # Format each sale record
         formatted_sales = []
         for sale in outgoing_sales:
                created_time = sale['created_at']
                formatted_sales.append({
                    "time": created_time.strftime("%Y-%m-%d %H:%M:%S"),
                    'soudi_hour': created_time.strftime("%I:%M %p"),
                    "amount": float(sale['total_amount']),
                    "month": calendar.month_name[created_time.month]
                })
         recent_logs = (
            LogEntry.objects.select_related("actor", "content_type")
            .filter(timestamp__year=year, timestamp__month=month)
            .order_by("-timestamp")[:10]
        )
         

         logs_serializer = HistoryTrackSerializer(recent_logs, many=True)
         
         return Response(
            {
               'clients':clients,
               'month_new_subscription':new_subscription,
               'month_sales':month_total_revenue,
               'month_new_added_building':total_building,
               'outgoing_sales': formatted_sales,
               'analitycs':analitycs,
               'recent_activity':logs_serializer.data,
               'top_clients':top_clients
               

            }
         )
         
from .models import  AdminProfileModel      
from .serializers import AdminProfileSerializer
from rest_framework import viewsets

from rest_framework.permissions import IsAdminUser
class AdminProfileViewSet(viewsets.ModelViewSet):
    queryset = AdminProfileModel.objects.all()
    permission_classes = [IsAdminUser]
    serializer_class = AdminProfileSerializer
   
class AdminUserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.filter(user_type='admin')
    permission_classes = [IsAdminUser]
    serializer_class = AdminUserSerializer



      



        