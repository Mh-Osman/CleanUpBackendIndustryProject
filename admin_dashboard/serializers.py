import calendar
from datetime import datetime
from rest_framework import serializers
from all_history.serializers import HistoryTrackSerializer

class DashBoardTopSerializer(serializers.Serializer):
    year = serializers.IntegerField(required=False)
    month = serializers.CharField()
    

    def validate_month(self, value):
        month_name = value.title()
        try:
            month_number = list(calendar.month_name).index(month_name)
        except ValueError:
            raise serializers.ValidationError(
                "Make sure the month name is valid. Recheck the month name."
            )
        return month_number  # returns integer month

    def validate_year(self, value):
        if value is None:
            value = datetime.now().year
        return value
   
from admin_dashboard.models import AdminProfileModel
from users.models import CustomUser
class AdminProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdminProfileModel
        fields = '__all__'
        
class AdminUserSerializer(serializers.ModelSerializer):
    admin_profile = AdminProfileSerializer(required=False)
    class Meta:
        model = CustomUser
        fields = ['id', 'name', 'email', 'prime_phone', 'is_active', 'date_joined','admin_profile']
        read_only_fields = ['id', 'date_joined']
    
    def create(self, validated_data):
        admin_profile_data = validated_data.pop('admin_profile', None)
        validated_data['user_type'] = 'admin'
        validated_data['is_active'] = True  # new admin active by default
        validated_data['password'] = 'admin123'  # default password, should be changed later
        user = CustomUser.objects.create_user(**validated_data)
        if admin_profile_data:
            AdminProfileModel.objects.create(user=user, **admin_profile_data)
        return user
    def update(self, instance, validated_data):
        admin_profile_data = validated_data.pop('admin_profile', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if admin_profile_data:
            AdminProfileModel.objects.update_or_create(user=instance, defaults=admin_profile_data)
        return instance
    
