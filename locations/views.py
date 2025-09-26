from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, permissions
from .models import Region, Building, Apartment
from .serializers import RegionSerializer, BuildingSerializer, ApartmentSerializer, BuildingpageSerializer
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework import generics
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

class RegionViewSet(viewsets.ModelViewSet):
    queryset = Region.objects.all()
    serializer_class = RegionSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['name', 'code']
    search_fields = ['name', 'code',]

class BuildingViewSet(viewsets.ModelViewSet):
    queryset = Building.objects.all()
    serializer_class = BuildingSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['name', 'code', 'region__name', 'region__code']
    search_fields = ['name', 'code', 'region__name', 'region__code']

class apartmentViewSet(viewsets.ModelViewSet):
    queryset = Apartment.objects.all()
    serializer_class = ApartmentSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['name', 'code', 'building__name', 'building__code', 'region__name', 'region__code']
    search_fields = ['name', 'code', 'building__name', 'building__code', 'region__name', 'region__code']
    


class BuildingListView(generics.ListAPIView):
    queryset = Building.objects.all()  # you can filter here if needed
    serializer_class = BuildingpageSerializer


class BuildingDetailView(generics.RetrieveAPIView):
    queryset = Building.objects.all()
    serializer_class = BuildingpageSerializer