from django.urls import path,include
from .views import   EmployeeViewSet, EmpployeeSalaryViewSet,EmployeeOverviewViewset
from .views import EmployeeViewSet, EmpployeeSalaryViewSet,EmployeeOverviewViewset,SupervisorsListViewSet
from rest_framework.routers import DefaultRouter
router = DefaultRouter()
router.register(r'employees', EmployeeViewSet, basename='employee')
router.register(r'salaries', EmpployeeSalaryViewSet, basename='employee-salary')
#router.register(r'employee-region-building-apartment', EmployeeRegionBuildingApartmentView, basename='employee-region-building-apartment')
router.register(r'supervisors',SupervisorsListViewSet, basename='supervisor')

urlpatterns = [
   path('', include(router.urls)),
   path('overview/',EmployeeOverviewViewset.as_view()),
 #  path('employee/building_page/', EmployeeDashboardBuildingPafeView.as_view()),
]