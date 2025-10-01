from rest_framework import viewsets, permissions
from .models import CustomUser
from .serializers import ClientSerializer

class ClientViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.filter(user_type='client')
    serializer_class = ClientSerializer
    permission_classes = [permissions.IsAuthenticated]

    filterset_fields = ['name', 'email']
    search_fields = ['name', 'email']
