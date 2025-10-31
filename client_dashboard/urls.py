from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ClientCheckoutFormViewSet
router = DefaultRouter()
router.register(r'client-checkout-forms', ClientCheckoutFormViewSet, basename='client-checkout-form')

urlpatterns = [
    path('', include(router.urls)),
]