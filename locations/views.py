from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, permissions
from .models import *   #Building , Apartment 
from .serializers import * # BuildingSerializer, ApartmentSerializer
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework import generics
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView


class BuildingViewSet(viewsets.ModelViewSet):
    queryset = Building.objects.prefetch_related('apartments').all()
    serializer_class = BuildingSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['name' , 'city', 'location' ]
    search_fields = ['name', 'city', 'location' ]

class ApartmentViewSet(viewsets.ModelViewSet):
    queryset = Apartment.objects.select_related('building', 'client').all()
    serializer_class = ApartmentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['apartment_number', 'building__name', 'client__name']
    search_fields = ['apartment_number', 'building__name', 'client__name']
    ordering_fields = ['apartment_number', 'building__name', 'client__name']
