from rest_framework import serializers
from users.models import CustomUser
from .models import EmployeeProfile, EmployeeSalary

class EmployeeProfileSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)  # <- read_only user field
    class Meta:
        model = EmployeeProfile
        fields = '__all__'


class EmployeeSalarySerializer(serializers.ModelSerializer):
    employee_detail = EmployeeProfileSerializer(source="employee.employee_profile", read_only=True)

    class Meta:
        model = EmployeeSalary
        fields = [
            'id', 'employee', 'employee_detail', 'month',
            'performance_bonus', 'deductions', 'total_paid',
            'paid_on', 'paid'
        ]
        extra_kwargs = {
            'employee': {'write_only': True},  # Only pass employee ID on create/update
            'total_paid': {'read_only': True},  # auto-calculated
            'paid': {'read_only': True},        # manage separately
        }
    
class EmployeeSimpleSerializer(serializers.ModelSerializer):
    employee_profile = EmployeeProfileSerializer(required=False)

    class Meta:
        model = CustomUser
        fields = [
            'id',
            'name',
            'email',
            'phone',
            'is_active',
            'date_joined',
            'employee_profile',
        ]
        read_only_fields = ['id', 'date_joined']

    # === CREATE ===
    def create(self, validated_data):
        validated_data['is_active'] = True
        validated_data['user_type'] = 'employee'

        profile_data = validated_data.pop("employee_profile", {}) or {}
        user = CustomUser.objects.create_user(**validated_data)
        EmployeeProfile.objects.create(user=user, **profile_data)
        return user

    # === UPDATE ===
    def update(self, instance, validated_data):
        profile_data = validated_data.pop('employee_profile', None)

        # Clean and unique check for email
        if 'email' in validated_data:
            email = (validated_data['email'] or '').strip()
            if CustomUser.objects.exclude(id=instance.id).filter(email__iexact=email).exists():
                raise serializers.ValidationError({
                    "email": "This email is already used."
                })
            validated_data['email'] = email

        # Clean and unique check for phone
        if 'phone' in validated_data:
            phone = (validated_data['phone'] or '').strip()
            if CustomUser.objects.exclude(id=instance.id).filter(phone=phone).exists():
                raise serializers.ValidationError({
                    "phone": "This phone is already used."
                })
            validated_data['phone'] = phone

        # Update user fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Handle employee profile
        if profile_data is not None:
            emp = EmployeeProfile.objects.filter(user=instance).first()

            if emp:
                # Handle unique NID check only if changed
                if 'national_id' in profile_data:
                    incoming_nid = (profile_data['national_id'] or '').strip()
                    current_nid = (emp.national_id or '').strip()
                    if current_nid == incoming_nid:
                        for attr, value in profile_data.items():
                            setattr(emp, attr, value)
                        emp.save()
                    if incoming_nid and incoming_nid != current_nid:
                        if EmployeeProfile.objects.exclude(id=emp.id).filter(national_id=incoming_nid).exists():
                            raise serializers.ValidationError({
                                "employee_profile": {
                                    "national_id": "This national id is already used. Profile update failed but user info was updated."
                                }
                            })

                for attr, value in profile_data.items():
                    setattr(emp, attr, value)
                emp.save()

            else:
                # Create new profile if missing
                EmployeeProfile.objects.create(user=instance, **profile_data)

        return instance