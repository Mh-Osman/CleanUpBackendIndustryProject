from rest_framework import serializers
from .models import EmployeeProfile, EmployeeSalary #Attendance,EmployeeApartmentAssignment
from users.models import CustomUser
# from invoice_request_from_client.models import InvoiceRequestFromEmployee
from plan.models import Subscription
from assign_task_employee.models import SpecialServicesModel
from rating.models import RatingModel
from django.db.models import Avg
class EmployeeProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeProfile
        fields = ['id', 'department', 'role', 'shift', 'is_on_leave', 'location', 'national_id', 'contact_number', 'location', 'contract_start', 'contract_end', 'base_salary']
        read_only_fields = ['contract_start']
        extra_kwargs = {
            'national_id': {'validators': []}  # DRF এর default UniqueValidator remove
        }


class EmployeeWithProfileSerializer(serializers.ModelSerializer):
    employee_profile = EmployeeProfileSerializer(required=False)

    tasks_completed = serializers.SerializerMethodField(read_only=True)
    client_rating = serializers.SerializerMethodField(read_only=True)
    total = serializers.SerializerMethodField(read_only=True)


    class Meta:
        model = CustomUser
        fields = ['id', 'name', 'email', 'prime_phone', 'is_active', 'date_joined', 'employee_profile', 'tasks_completed' , 'client_rating' , 'total']
        read_only_fields = ['id', 'date_joined']
    def validate(self, attrs):
        profile_data = attrs.get('employee_profile')
        if profile_data:
            nid = profile_data.get('national_id')
            user_id = self.instance.id if self.instance else None
            if EmployeeProfile.objects.exclude(user__id=user_id).filter(national_id=nid).exists():
                raise serializers.ValidationError({
                    "employee_profile": {"national_id": "employee profile with this national id already exists."}
                })
        return attrs
    

    def validate_national_id(self, value):
        value = value.strip()
        user_id = self.instance.id if self.instance else None
        if EmployeeProfile.objects.filter(national_id=value).exclude(user__id=user_id).exists():
            raise serializers.ValidationError("National ID already in use.")
        return value
    
    def create(self, validated_data):
        profile_data = validated_data.pop('employee_profile', {})
        validated_data['user_type'] = 'employee'
        validated_data['is_active'] = True  # new employee active by default
        validated_data['password'] = '12345'  # default password, should be changed later
        user = CustomUser.objects.create_user(**validated_data)

        # create profile
        EmployeeProfile.objects.create(user=user, **profile_data)
        return user

    def update(self, instance, validated_data):
        profile_data = validated_data.pop('employee_profile', None)

        # Update main CustomUser fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Update or create EmployeeProfile without validation
        if profile_data:
            profile_instance, created = EmployeeProfile.objects.get_or_create(user=instance)
            for attr, value in profile_data.items():
                setattr(profile_instance, attr, value)
            profile_instance.save()

        return instance
    

    def get_tasks_completed(self, obj):
        assigned_subscriptions = Subscription.objects.filter(employee=obj, status='past_due').count()
        special_services = SpecialServicesModel.objects.filter(worker=obj, status='completed').count()

        return assigned_subscriptions + special_services
    
    def get_client_rating(self, obj):
        ratings = RatingModel.objects.filter(employee=obj)
        if ratings.exists():
            return round(ratings.aggregate(Avg('rating'))['rating__avg'], 2)
        return None
    
    def get_total(self, obj):
        return SpecialServicesModel.objects.filter(worker=obj).count() + Subscription.objects.filter(employee=obj).count()


class EmployeeSalarySerializer(serializers.ModelSerializer):
    employee = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.filter(user_type='employee'), required=True)
    class Meta:
        model = EmployeeSalary
        fields = '__all__'
        read_only_fields = ['id', 'total_paid', 'paid_on']  # total_paid auto, paid_on auto
    # def validate_month(self, value):
    #     from django.utils import timezone
    #     if value > timezone.now().date():
    #         raise serializers.ValidationError("Month cannot be in the future.")
    #     return value
    
    def create(self, validated_data):
        from django.utils import timezone

        # default month
        if 'month' not in validated_data or validated_data['month'] is None:
            validated_data['month'] = timezone.now().date().replace(day=1)
        month_date = validated_data['month']
        # check duplicate
        if EmployeeSalary.objects.filter(employee=validated_data['employee'],  month__year=month_date.year,
        month__month=month_date.month).exists():
            raise serializers.ValidationError(
                    {
                        "message": "Salary for this employee for the specified month already exists."
                    }
                    )

        # create and return the instance
        salary = EmployeeSalary.objects.create(**validated_data)
        return salary






class EmployOverView(serializers.Serializer):
    active = serializers.SerializerMethodField(read_only=True)
    leave = serializers.SerializerMethodField(read_only=True)
    total_payroll = serializers.SerializerMethodField(read_only=True)
    average_performance=serializers.SerializerMethodField(read_only=True)



