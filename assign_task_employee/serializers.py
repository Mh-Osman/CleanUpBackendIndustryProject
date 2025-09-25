from rest_framework import serializers
from .models import TaskAssignToEmployee
from locations.models import Building, Apartment
from services_pakages.models import Category
from django.contrib.auth import get_user_model
from services_pakages.serializers import CategorySerializer
User = get_user_model()


class TaskAssignToEmployeeSerializer(serializers.ModelSerializer):
    category=CategorySerializer(many=True)
    class Meta:
        model = TaskAssignToEmployee
        fields = [
            "id",
            "name",
            "task_code",
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
        ]
        read_only_fields = ["created_at", "updated_at","id"]
