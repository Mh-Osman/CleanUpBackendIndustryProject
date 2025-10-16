from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import  ApartmentViewSet, BuildingViewSet , RegionViewSet, location_overview # Import your viewsets here
router = DefaultRouter()
router.register(r'buildings', BuildingViewSet)
router.register(r'apartments', ApartmentViewSet)
router.register(r'regions', RegionViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('locations/overview/', location_overview, name='location-overview'),

]