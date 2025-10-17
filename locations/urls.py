from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import  ApartmentViewSet, BuildingViewSet, RegionDetailViewSet , RegionViewSet, location_overview # Import your viewsets here
router = DefaultRouter()
router.register(r'buildings', BuildingViewSet)
router.register(r'apartments', ApartmentViewSet)
router.register(r'regions', RegionViewSet)
router.register(r'regionlist', RegionDetailViewSet, basename='regionlist')


urlpatterns = [
    path('', include(router.urls)),
    path('locations/overview/', location_overview, name='location-overview'),
    
    
]