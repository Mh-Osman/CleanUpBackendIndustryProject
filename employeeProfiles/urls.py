from django.urls import path,include
from .views import  EmployeeViewSet, EmpployeeSalaryViewSet,EmployeeOverviewViewset
from .views import EmployeeViewSet, EmpployeeSalaryViewSet,EmployeeOverviewViewset
from rest_framework.routers import DefaultRouter
router = DefaultRouter()
router.register(r'employees', EmployeeViewSet, basename='employee')
router.register(r'salaries', EmpployeeSalaryViewSet, basename='employee-salary')
#router.register(r'employee-region-building-apartment', EmployeeRegionBuildingApartmentView, basename='employee-region-building-apartment')

urlpatterns = [
   path('', include(router.urls)),
   path('overview/',EmployeeOverviewViewset.as_view()),
]