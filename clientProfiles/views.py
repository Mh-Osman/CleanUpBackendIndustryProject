# views.py
from rest_framework import viewsets
from users.models import CustomUser
from .serializers import ClientSerializer
from rest_framework.permissions import IsAdminUser

class ClientViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.filter(role='client').select_related('client_profile')
    serializer_class = ClientSerializer
    permission_classes = [IsAdminUser]
    