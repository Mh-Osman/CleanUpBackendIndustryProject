from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, permissions
from .models import LeaseFormModel
from .serializers import LeaseFormSerializer
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticated, IsAdminUser
class LeaseFormViewSet(viewsets.ModelViewSet):
    queryset = LeaseFormModel.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = LeaseFormSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = []  # Add any filter fields if needed
    search_fields = []  # Add any search fields if needed
    ordering_fields = []  # Add any ordering fields if needed
   