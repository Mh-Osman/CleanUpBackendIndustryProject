from rest_framework import viewsets
from .models import CustomUser,EmployeeSalary, EmployeeProfile
from rest_framework.response import Response 
from rest_framework import status, decorators, response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from .serializers import EmployeeWithProfileSerializer , EmployeeSalarySerializer
from rest_framework.permissions import IsAdminUser



class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.filter(user_type='employee')

    serializer_class = EmployeeWithProfileSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['name', 'email', 'employee_profile__department', 'employee_profile__role']
    search_fields = ['name', 'email', 'employee_profile__national_id', 'employee_profile__contact_number']

class EmpployeeSalaryViewSet(viewsets.ModelViewSet):
    queryset = EmployeeSalary.objects.all()
    serializer_class = EmployeeSalarySerializer
    permission_classes = [IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['employee__name', 'employee_id','month', 'paid']
    serch_fields = ['employee__name', 'employee_id']
    
    # Custom update by employee + month
    @decorators.action(detail=False, methods=["put", "patch"], url_path="update-by-employee")
    def update_by_employee(self, request):
        employee_id = request.data.get("employee_id")
        month = request.data.get("month")
        if not employee_id or not month:
            return response.Response({"error": "employee_id and month are required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            salary = EmployeeSalary.objects.get(employee_id=employee_id, month=month)
        except EmployeeSalary.DoesNotExist:
            return response.Response({"error": "Salary not found for this employee in given month"}, status=status.HTTP_404_NOT_FOUND)

        data = request.data.copy()
        data.pop("employee", None)
        data.pop("employee_id", None)
        data.pop("month", None)

        serializer = self.get_serializer(salary, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return response.Response(serializer.data, status=status.HTTP_200_OK)

    # Optional: latest salary per employee
    @decorators.action(detail=False, methods=["get"], url_path="latest-by-employee/(?P<employee_id>[^/.]+)")
    def latest_by_employee(self, request, employee_id=None):
        salary = EmployeeSalary.objects.filter(employee_id=employee_id).order_by('-month').first()
        if not salary:
            return response.Response({"error": "No salary found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(salary)
        return response.Response(serializer.data)