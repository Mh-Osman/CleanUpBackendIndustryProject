from django.urls import path,include
from .views import LeaseFormViewSet, SupervisorFormViewSet , supervisor_form_list
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'lease-forms', LeaseFormViewSet)
router.register(r'supervisor-forms', SupervisorFormViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('supervisor-forms-list/', supervisor_form_list, name='supervisor-form-list'),
   
]
