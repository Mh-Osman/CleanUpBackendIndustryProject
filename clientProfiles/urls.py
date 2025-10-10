from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ClientViewSet, ClientPhoneViewSet,admin_dashboard_clients_display

router = DefaultRouter()
router.register(r'clients', ClientViewSet)
router.register(r'clientphones', ClientPhoneViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('admin-dashboard-clients/', admin_dashboard_clients_display, name='admin-dashboard-clients'),
]
