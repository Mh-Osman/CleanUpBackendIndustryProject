# employees/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EmployeeSalaryViewSet, EmployeeViewSet, EmployeeProfileViewSet

router = DefaultRouter()
router.register(r'employees', EmployeeViewSet, basename='employee')
router.register(r'employee-profiles', EmployeeProfileViewSet, basename='employee-profile')
router.register(r'employee-salaries', EmployeeSalaryViewSet, basename='employee-salary')

urlpatterns = [
    path('', include(router.urls)),
]