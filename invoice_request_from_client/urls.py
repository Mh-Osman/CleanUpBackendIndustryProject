from .views import InvoiceRequestFromEmployeeView
from django.urls import path,include
from rest_framework.routers import DefaultRouter


router=DefaultRouter()
router.register('list',InvoiceRequestFromEmployeeView,basename='invoice-request')

urlpatterns = [
    path('',include(router.urls)),
]
