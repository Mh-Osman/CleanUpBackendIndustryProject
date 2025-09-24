# employees/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EmployeeViewSet, EmployeeProfileViewSet, EmployeeSalaryViewSet 

router = DefaultRouter()
router.register(r'employees', EmployeeViewSet, basename='employee')
router.register(r'employee-profiles', EmployeeProfileViewSet, basename='employeeprofile')
router.register(r'employee-salaries', EmployeeSalaryViewSet, basename='employeesalary')




urlpatterns = [
    path('', include(router.urls)),
    
]