from django.urls import path,include
from .views import LeaseFormViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'lease-forms', LeaseFormViewSet)

urlpatterns = [
    path('', include(router.urls)),
   
]
