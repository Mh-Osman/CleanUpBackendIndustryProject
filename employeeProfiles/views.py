from rest_framework import viewsets, permissions, filters, serializers  
from .models import CustomUser, EmployeeProfile, EmployeeSalary
from .serializers import EmployeeSimpleSerializer,EmployeeProfileSerializer, EmployeeSalarySerializer
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404

class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.filter(user_type='employee').select_related('employee_profile')
    serializer_class = EmployeeSimpleSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'email', 'employee_profile__department']
    ordering_fields = ['date_joined']




class EmployeeProfileViewSet(viewsets.ModelViewSet):
    queryset = EmployeeProfile.objects.filter(user__user_type='employee')
    serializer_class = EmployeeProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

class EmployeeSalaryViewSet(viewsets.ModelViewSet):
    queryset = EmployeeSalary.objects.select_related('employee', 'employee__employee_profile').all()
    serializer_class = EmployeeSalarySerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['employee__name', 'employee__email', 'month']
    ordering_fields = ['month', 'total_paid', 'performance_bonus']

    


    # Custom get_object to fetch by employee and month
    def get_object(self):
        employee_id = self.kwargs.get('employee_id')
        month = self.request.data.get('month')
        if employee_id and month:
            obj = get_object_or_404(EmployeeSalary, employee_id=employee_id, month=month)
            self.check_object_permissions(self.request, obj)
            return obj
        return super().get_object()
    
    def partial_update(self, request, *args, **kwargs):
        """PATCH request support করার জন্য"""
        kwargs['partial'] = True  # partial update enable
        return self.update(request, *args, **kwargs)
