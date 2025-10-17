from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, permissions
from .models import Building , Apartment , Region 
from .serializers import * # BuildingSerializer, ApartmentSerializer
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework import generics
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from plan.models import Subscription
from assign_task_employee.models import SpecialServicesModel
from rating.models import RatingModel
from plan.models import PlanModel
from rest_framework.decorators import api_view, permission_classes
from rest_framework import permissions
from rest_framework.response import Response
from django.db.models import Avg
class RegionViewSet(viewsets.ModelViewSet):
    queryset = Region.objects.all()
    serializer_class = RegionSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['name']
    search_fields = ['name']

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

@api_view(['GET'])
@permission_classes([permissions.IsAdminUser])
def location_overview(request):
    total_active_apartments = (
        Subscription.objects.filter(status='active')
        .exclude(apartment__isnull=True)
        .values('apartment')
        .distinct()
        .count()
    )

    total_buildings = Building.objects.count()
    total_apartments = Apartment.objects.count()
    total_inactive_apartments = (
        Apartment.objects.count() - total_active_apartments
    )


    return Response({
        "total_buildings": total_buildings,
        "total_apartments": total_apartments,
        "total_active_apartments": total_active_apartments,
        "total_inactive_apartments": total_inactive_apartments
    })


class RegionDetailViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Returns all regions with nested buildings, or a single region by ID.
    """
    queryset = Region.objects.all()
    serializer_class = RegionDetailSerializer
    permission_classes = [IsAuthenticated]
