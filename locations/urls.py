from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ApartmentViewSet,
    BuildingViewSet,
    EmployeeInMapViewset,
    RegionCodeAndClientCodeFilterViewSet,
 
    # EmployeeinMapViewset1,
    RegionDetailViewSet,
    RegionViewSet,
    # EmployeeInMapViewset2,
)

from .views import location_overview, BuilgingByRegionIdList


router = DefaultRouter()
router.register(r'buildings', BuildingViewSet)
router.register(r'apartments', ApartmentViewSet)
router.register(r'regions', RegionViewSet)
router.register(r'regionlist', RegionDetailViewSet, basename='regionlist')
# router.register(r'test', EmployeeinMapViewset, basename='location')
# router.register(r'test1', EmployeeinMapViewset1, basename='location1')
router.register(r'location_details_according_active_task', EmployeeInMapViewset, basename='location2')
router.register(r'search_apartment_by_region_client', RegionCodeAndClientCodeFilterViewSet, basename='region-code-client-code-filter')
urlpatterns = [
    path('', include(router.urls)),
    path('locations/overview/', location_overview, name='location-overview'),  # e.g. /api/locations/location/overview/
    path('buildings/region/<int:region_id>/', BuilgingByRegionIdList, name='buildings-by-region'),  # e.g. /api/locations/buildings/by-region/1/
  
]