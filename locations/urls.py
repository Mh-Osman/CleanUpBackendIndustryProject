from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import  ApartmentViewSet, BuildingViewSet  # Import your viewsets here
router = DefaultRouter()
router.register(r'buildings', BuildingViewSet)
router.register(r'apartments', ApartmentViewSet)

urlpatterns = [
    path('', include(router.urls)),

]