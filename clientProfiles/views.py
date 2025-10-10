
from rest_framework import viewsets, permissions
from .models import ClientPhone, CustomUser
from .serializers import ClientSerializer, ClientPhoneSerializer, AdminDashboardClientDisplaySerializer
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from rest_framework import status


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


#admindashboard client part #first api (total client , rating , revenue ,optional)
#fucntion based view
from rest_framework.decorators import api_view, permission_classes
@api_view(['GET'])
# @permission_classes([permissions.IsAuthenticated])
@permission_classes([permissions.AllowAny])
def admin_dashboard_clients_display(request):
    clients = CustomUser.objects.filter(user_type='client')
   

    data = {
        "client_details": clients,
        "client_phones": phones,
    }

    serializer = AdminDashboardClientDisplaySerializer(clients, many=True)
    return Response(serializer.data)

   
