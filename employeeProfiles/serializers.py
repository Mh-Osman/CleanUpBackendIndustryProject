from rest_framework import serializers
from users.models import CustomUser
from .models import EmployeeProfile, EmployeeSalary

class EmployeeProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeProfile
        fields = '__all__'


class EmployeeSalarySerializer(serializers.ModelSerializer):
    # nested detail শুধু read-only আকারে থাকবে
   # employee_detail = EmployeeProfileSerializer(source="employee.employee_profile", read_only=True)
    

    class Meta:
        model = EmployeeSalary
        fields = [
            'id', 'month', 'base_salary', 'performance_bonus', 'deductions',
            'total_paid', 'paid_on', 'employee',
        ]
        extra_kwargs = {
            'employee': {'write_only': True}   # create/update করার সময় শুধু employee id দিবে
        }


class EmployeeSerializer(serializers.ModelSerializer):
    employee_profile = EmployeeProfileSerializer(required=False)
    salaries = EmployeeSalarySerializer(many=True, required=False)

    department = serializers.CharField(source='employee_profile.department', allow_blank=True, required=False)
    role = serializers.CharField(source='employee_profile.role', allow_blank=True, required=False)
    national_id = serializers.CharField(source='employee_profile.national_id', allow_blank=True, required=False)
    id_expiry = serializers.DateField(source='employee_profile.id_expiry', allow_null=True, required=False)
    contact_number = serializers.CharField(source='employee_profile.contact_number', allow_blank=True, required=False)
    salary_day = serializers.IntegerField(source='employee_profile.salary_day', allow_null=True, required=False)
    shift = serializers.CharField(source='employee_profile.shift', allow_blank=True, required=False)
    location = serializers.CharField(source='employee_profile.location', allow_blank=True, required=False)
    avatar = serializers.ImageField(source='employee_profile.avatar', allow_null=True, required=False)
    base_salary = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)

    class Meta:
        model = CustomUser
        fields = [
            'id', 'name', 'email', 'phone', 'is_active', 'date_joined',
            'location', 'department', 'role', 'national_id', 'id_expiry',
            'contact_number', 'salary_day', 'avatar', 'shift', 'base_salary',
            'employee_profile', 'salaries'
        ]
        read_only_fields = ['id', 'date_joined']

    def create(self, validated_data):
        validated_data['is_active'] = True
        validated_data['user_type'] = 'employee'

        profile_data = validated_data.pop("employee_profile", None) or {}
        profile_data.setdefault("department", validated_data.pop("department", "Cleaning"))
        profile_data.setdefault("shift", validated_data.pop("shift", "morning"))
        profile_data.setdefault("location", validated_data.pop("location", ""))
        profile_data.setdefault("avatar", validated_data.pop("avatar", None))
        profile_data.setdefault("role", validated_data.pop("role", "Cleaner"))
        profile_data.setdefault("national_id", validated_data.pop("national_id", ""))
        profile_data.setdefault("id_expiry", validated_data.pop("id_expiry", None))
        profile_data.setdefault("contact_number", validated_data.pop("contact_number", ""))
        profile_data.setdefault("salary_day", validated_data.pop("salary_day", None))
        

        salaries_data = validated_data.pop("salaries", [])
        base_salary = validated_data.pop("base_salary", None)

        from django.utils.timezone import now
        if base_salary:
            salaries_data.append({
                "base_salary": base_salary,
                "month": now().date().replace(day=1)
            })

        user = CustomUser.objects.create_user(**validated_data)

        EmployeeProfile.objects.create(user=user, **profile_data)

        for sd in salaries_data:
            EmployeeSalary.objects.create(employee=user, **sd)

        return user
