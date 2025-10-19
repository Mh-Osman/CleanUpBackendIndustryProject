from django.urls import path,include
from .views import LeaseFormViewSet, SupervisorFormViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'lease-forms', LeaseFormViewSet)
router.register(r'supervisor-forms', SupervisorFormViewSet)

urlpatterns = [
    path('', include(router.urls)),
   
]
