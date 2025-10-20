from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import  ApartmentViewSet, BuildingViewSet, EmployeeinMapViewset, EmployeeinMapViewset1, RegionDetailViewSet , RegionViewSet # Import your viewsets here
router = DefaultRouter()
router.register(r'buildings', BuildingViewSet)
router.register(r'apartments', ApartmentViewSet)
router.register(r'regions', RegionViewSet)
router.register(r'regionlist', RegionDetailViewSet, basename='regionlist')
router.register(r'test', EmployeeinMapViewset, basename='location')
router.register(r'test1', EmployeeinMapViewset1, basename='location1')
urlpatterns = [
    path('', include(router.urls)),
  
    
    
]