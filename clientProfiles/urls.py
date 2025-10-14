from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ClientViewSet, ClientPhoneViewSet
router = DefaultRouter()
router.register(r'clients', ClientViewSet)
router.register(r'clientphones', ClientPhoneViewSet)

urlpatterns = [
    path('', include(router.urls)),
  
]
