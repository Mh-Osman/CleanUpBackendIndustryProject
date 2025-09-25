from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, permissions
from .models import Region, Building, Apartment
from .serializers import RegionSerializer, BuildingSerializer, ApartmentSerializer
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticated, IsAdminUser

class RegionViewSet(viewsets.ModelViewSet):
    queryset = Region.objects.all()
    serializer_class = RegionSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['name', 'code']
    search_fields = ['name', 'code']