from rest_framework import serializers
from .models import TaskAssignToEmployee
from locations.models import Building, Apartment
from locations.serializers import BuilingSerializer
from services_pakages.models import Category
from django.contrib.auth import get_user_model
from services_pakages.serializers import CategorySerializer
from .models import FeatureModel
from django.db.models import Sum
User = get_user_model()


class TaskAssignToEmployeeSerializer(serializers.ModelSerializer):
    # category=CategorySerializer(many=True)
    # building=BuilingSerializer(read_only=True)
    active=serializers.SerializerMethodField(read_only=True)
    total_revenue=serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = TaskAssignToEmployee
        fields = [
            "id",
            "name",
            "plan",
            "description",
            "category",
            "base_price",
            "bill_cycle",
            "discount",
            "tax_rate",
            "building",
            "auto_renew_enable",
            "worker",
            "created_at",
            "updated_at",
            "service_icon",
            "status",
            "apratment",
            "package",
            'total_revenue',
            'active',
        ]
        read_only_fields = ["created_at", "updated_at","id"]

    def get_active(self,obj):
        return TaskAssignToEmployee.objects.filter(status='started').count()
    def get_total_revenue(self, obj):
        total = TaskAssignToEmployee.objects.filter(id=obj.id, status='completed').aggregate(
            total_amount=Sum('base_price')
        )['total_amount']
        return total or 0

class FeatureSerialzer(serializers.ModelSerializer):
    class Meta:
        model=FeatureModel
        fields='__all__'

class ServiceDetailsSerializer(serializers.ModelSerializer):
    category=CategorySerializer(read_only=True,many=True)
    building=BuilingSerializer(read_only=True)
    package=FeatureSerialzer(read_only=True,many=True)
    active=serializers.SerializerMethodField(read_only=True)
    completed=serializers.SerializerMethodField(read_only=True)
    revenue=serializers.SerializerMethodField(read_only=True)
    pending=serializers.SerializerMethodField()
    total_booking=serializers.SerializerMethodField(read_only=True)
    

    class Meta:
        model=TaskAssignToEmployee
        fields = [
            "id",
            "name",
            "plan",
            "description",
            "category",
            "base_price",
            "bill_cycle",
            "discount",
            "tax_rate",
            "building",
            "auto_renew_enable",
            "worker",
            "created_at",
            "updated_at",
            "service_icon",
            "status",
            "apratment",
            "package",
            'status',
            'revenue',
            'package',
            'total_booking',
            'active',
            'completed',
            'pending',
        ]

   

    def get_active(self,obj):
        return TaskAssignToEmployee.objects.filter(id=obj.id,status='started').count()
    def get_completed(self,obj):
        return TaskAssignToEmployee.objects.filter(id=obj.id,status='completed').count()
    def get_pending(self,obj):
        return TaskAssignToEmployee.objects.filter(id=obj.id,status='pending').count()
    def get_revenue(self, obj):
        
        total = TaskAssignToEmployee.objects.filter(id=obj.id, status='completed').aggregate(
            total_amount=Sum('base_price')
        )['total_amount']
        return total or 0

    def get_total_booking(self, obj):
        return TaskAssignToEmployee.objects.filter(id=obj.id).count()
