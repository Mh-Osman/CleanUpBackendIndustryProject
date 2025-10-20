from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ApartmentViewSet,
    BuildingViewSet,
    EmployeeInMapViewset,
    # EmployeeinMapViewset1,
    RegionDetailViewSet,
    RegionViewSet,
    # EmployeeInMapViewset2,
)


router = DefaultRouter()
router.register(r'buildings', BuildingViewSet)
router.register(r'apartments', ApartmentViewSet)
router.register(r'regions', RegionViewSet)
router.register(r'regionlist', RegionDetailViewSet, basename='regionlist')
# router.register(r'test', EmployeeinMapViewset, basename='location')
# router.register(r'test1', EmployeeinMapViewset1, basename='location1')
router.register(r'location_details_according_active_task', EmployeeInMapViewset, basename='location2')
urlpatterns = [
    path('', include(router.urls)),
  
]