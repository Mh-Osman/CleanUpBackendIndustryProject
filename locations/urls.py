from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RegionViewSet, BuildingViewSet, apartmentViewSet

router = DefaultRouter()
router.register(r'regions', RegionViewSet)
router.register(r'buildings', BuildingViewSet)
router.register(r'apartments', apartmentViewSet)

urlpatterns = [
    path('', include(router.urls)),
]