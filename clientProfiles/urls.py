from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ClientViewSet, ClientPhoneViewSet,client_overview
router = DefaultRouter()
router.register(r'clients', ClientViewSet)
router.register(r'clientphones', ClientPhoneViewSet)

urlpatterns = [
    path('clients/overview/', client_overview, name='client-overview'),
    path('', include(router.urls)),

  
]
