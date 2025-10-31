from .models import ClientCheckoutForm
from rest_framework import serializers
from plan.models import Subscription
from users.models import CustomUser
from assign_task_employee.models import SpecialServicesModel

class ClientCheckoutFormSerializer(serializers.ModelSerializer):
      
    subscription = serializers.PrimaryKeyRelatedField(
        queryset=Subscription.objects.all(),
        required=False,
        allow_null=True
    )
    special_service = serializers.PrimaryKeyRelatedField(
        queryset=SpecialServicesModel.objects.all(),
        required=False,
        allow_null=True
    )
    class Meta:
        model = ClientCheckoutForm
        fields = [
            'id',
            'form_name',
            'client',
            'subscription',
            'special_service',
            'set_time',
            'time_range',
            'form_type',
            'description',
        ]

