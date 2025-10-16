
from rest_framework import viewsets, permissions

from admin_dashboard import serializers
from .models import ClientPhone, CustomUser
from .serializers import ClientSerializer, ClientPhoneSerializer
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from rest_framework import status

from plan.models import Subscription
from assign_task_employee.models import SpecialServicesModel
from rating.models import RatingModel
from plan.models import PlanModel
class ClientProfileViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.filter(user_type='client')
    serializer_class = ClientSerializer
  #  permission_classes = [permissions.IsAuthenticated]
    permission_classes = [permissions.AllowAny]

    filterset_fields = ['name', 'email', 'prime_phone']
    search_fields = ['name', 'email', 'prime_phone']

class ClientPhoneViewSet(viewsets.ModelViewSet):
    queryset = ClientPhone.objects.all()
    serializer_class = ClientPhoneSerializer
  #  permission_classes = [permissions.IsAuthenticated]
    permission_classes = [permissions.AllowAny]
    filterset_fields = ['phone_number']
    search_fields = ['phone_number']

class ClientViewSet(viewsets.ModelViewSet):
    # queryset = CustomUser.objects.filter(user_type='client')
    queryset = CustomUser.objects.select_related('client_profile').filter(user_type='client')
    
    serializer_class = ClientSerializer
   # permission_classes = [permissions.IsAuthenticated]
    permission_classes = [permissions.AllowAny]
    filterset_fields = ['name', 'email', 'prime_phone']
    search_fields = ['name', 'email', 'prime_phone']
from rest_framework.decorators import api_view, permission_classes
from rest_framework import permissions
from rest_framework.response import Response
from django.db.models import Avg
@api_view(['GET'])
@permission_classes([permissions.IsAdminUser])
def client_overview(request):
    # Count total services
    special_services_count = SpecialServicesModel.objects.count()
    subscriptions_count = Subscription.objects.count()
    total_services = special_services_count + subscriptions_count

    # Count active bookings
    active_special_services = SpecialServicesModel.objects.filter(
        status__in=['started', 'pending']
    ).count()
    active_subscriptions = Subscription.objects.filter(status='active').count()
    total_active_booking = active_special_services + active_subscriptions

    # Calculate total client payments (assumes `amount` field exists)
    total_client_pay = sum(
        subscription.plan.amount for subscription in Subscription.objects.all()
    )

    client_rating = RatingModel.objects.aggregate(Avg('rating'))['rating__avg'] or 2.5
    client_rating = round(client_rating, 2)

    total_client = CustomUser.objects.filter(user_type='client').count()

    return Response({
        "total_services": total_services,
        "active_booking": total_active_booking,
        "total_client_pay": total_client_pay,
        "client_rating": client_rating,
        "total_client": total_client
    })


