from rest_framework import viewsets, permissions, filters, serializers
from .models import EmployeeProfile, EmployeeSalary
from .serializers import EmployeeProfileSerializer, EmployeeSerializer, EmployeeSalarySerializer
from users.models import CustomUser

class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.filter(role='employee').select_related('employee_profile')
    serializer_class = EmployeeSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'email', 'employee_profile__department']
    ordering_fields = ['date_joined']


class EmployeeSalaryViewSet(viewsets.ModelViewSet):
    queryset = EmployeeSalary.objects.select_related('employee').all()
    serializer_class = EmployeeSalarySerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]

    search_fields = ['employee__name', 'employee__email', 'employee__employee_profile__department', 'month']
    ordering_fields = ['month', 'base_salary', 'total_paid']

    def perform_create(self, serializer):
        employee_id = self.request.data.get("employee")
        if not employee_id:
            raise serializers.ValidationError({"employee": "Employee id is required"})
        serializer.save(employee_id=employee_id)  # ✅ এখানে employee field ঠিকভাবে সেট হচ্ছে


class EmployeeProfileViewSet(viewsets.ModelViewSet):
    queryset = EmployeeProfile.objects.filter(user__role='employee')
    serializer_class = EmployeeProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
