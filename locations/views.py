from urllib import request
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

# from rest_framework.decorators import api_view    
# @api_view(['GET'])
# def employee_in_map(request):
  
#     user = request.user
#     list_from_subscription = Subscription.objects.filter(
#         status='active', worker=user
#     ).select_related('apartment__building__region')

#     list_from_special_service = SpecialServicesModel.objects.filter(
#         status__in=['pending', 'started'], worker=user
#     ).select_related('apartment__building__region')

from django.db.models import Q
from .serializers import EmployeeInMapSerializer
# class EmployeeinMapViewset(viewsets.ViewSet):
#     permission_classes = [IsAuthenticated]

#     def list(self, request):
#         user = request.user

#         # Get region IDs from Subscription
#         subscription_region_ids = Subscription.objects.filter(
#             employee=user
#         ).values_list('apartment__building__region__id', flat=True)

#         # Get region IDs from SpecialServicesModel
#         special_service_region_ids = SpecialServicesModel.objects.filter(
#             worker=user
#         ).values_list('apartment__building__region__id', flat=True)

#         # Combine IDs and remove duplicates
#         region_ids = set(list(subscription_region_ids) + list(special_service_region_ids))

#         # Base queryset
#         regions = Region.objects.prefetch_related('buildings').filter(id__in=region_ids)

#         # Apply search if query parameter exists
#         search_query = request.GET.get('search', None)
#         if search_query:
#             regions = regions.filter(
#                 Q(name__icontains=search_query) |  # region name
#                 Q(buildings__name__icontains=search_query) |  # building name
#                 Q(buildings__location__icontains=search_query)  # building location
#             ).distinct()  # distinct to avoid duplicates due to joins

#         serializer = EmployeeInMapSerializer(regions, many=True, context={'user': user})
#         return Response(serializer.data)


# class EmployeeinMapViewset1(viewsets.ViewSet):
#     permission_classes = [IsAuthenticated]
#    # permission_classes = [AllowAny]

#     def list(self, request):
#         user = request.user
#         subscription_region_ids = Subscription.objects.filter(
#             employee=user
#         ).values_list('apartment', flat=True)

#         special_service_region_ids = SpecialServicesModel.objects.filter(
#             worker=user
#         ).values_list('apartment', flat=True)

#         apartment_ids = set(list(subscription_region_ids) + list(special_service_region_ids))

#         apartments = Apartment.objects.select_related('building__region').filter(id__in=apartment_ids)

#         serializer = EmployeeInMapSerializer1(apartments, many=True, context={'user': user})
#         return Response(serializer.data)



class EmployeeInMapViewset(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        user = request.user

        # Get query params for search and filtering
        search = request.query_params.get('search', None)  # general search
       # city_filter = request.query_params.get('city', None)
        type_filter = request.query_params.get('type', None)
        region_filter = request.query_params.get('region', None)

        # Get buildings related to user subscriptions and special services
        building_ids = set(
            Subscription.objects.filter(employee=user, status='active')
            .values_list('building', flat=True)
        ) | set(
            SpecialServicesModel.objects.filter(worker=user, status__in=['pending', 'started'])
            .values_list('building', flat=True)
        )

        buildings = Building.objects.filter(id__in=building_ids)

        # Apply general search
        if search:
            buildings = buildings.filter(
                Q(name__icontains=search) |
               # Q(city__icontains=search) |
                Q(location__icontains=search) |
                Q(region__name__icontains=search)
            )

        # Apply individual filters
        # if city_filter:
        #     buildings = buildings.filter(city__iexact=city_filter)
        if type_filter:
            buildings = buildings.filter(type__iexact=type_filter)
        if region_filter:
            buildings = buildings.filter(region__name__iexact=region_filter)

        # Prefetch apartments and region to reduce queries
        buildings = buildings.select_related('region').prefetch_related('apartments')

        serializer = EmployeeInMapSerializer(buildings, many=True, context={'user': user})
        return Response(serializer.data)

