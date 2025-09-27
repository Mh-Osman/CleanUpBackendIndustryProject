from rest_framework import viewsets, permissions
from .models import CustomUser
from .serializers import ClientSerializer
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend


class ClientProfileViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.filter(user_type='client')
    serializer_class = ClientSerializer
    permission_classes = [permissions.IsAuthenticated]

    filterset_fields = ['name', 'email']
    search_fields = ['name', 'email']

class ClientViewSet(viewsets.ModelViewSet):
    # queryset = CustomUser.objects.filter(user_type='client')
    queryset = CustomUser.objects.select_related('client_profile').filter(user_type='client')
    serializer_class = ClientSerializer
    permission_classes = [permissions.IsAuthenticated]

    filterset_fields = ['name', 'email']
    search_fields = ['name', 'email']
