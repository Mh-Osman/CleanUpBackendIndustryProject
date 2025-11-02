from .models import ClientCheckoutForm
from rest_framework import serializers
from plan.models import Subscription
from users.models import CustomUser
from assign_task_employee.models import SpecialServicesModel

class ClientCheckoutFormSerializer(serializers.ModelSerializer):

    subscription_building_name = serializers.SerializerMethodField()
    subscription_apartment_number = serializers.SerializerMethodField()
    service_building_name = serializers.SerializerMethodField()
    service_apartment_number = serializers.SerializerMethodField()

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
            'subscription_building_name',
            'subscription_apartment_number',
            'service_building_name',
            'service_apartment_number',
        ]

    # Subscription fields
    def get_subscription_building_name(self, obj):
        if obj.subscription:
            return obj.subscription.building_name  # adjust field name according to your model
        return None

    def get_subscription_apartment_number(self, obj):
        if obj.subscription:
            return obj.subscription.apartment_number  # adjust field name
        return None

    # Special service fields
    def get_service_building_name(self, obj):
        if obj.special_service:
            return obj.special_service.building_name  # adjust field name
        return None

    def get_service_apartment_number(self, obj):
        if obj.special_service:
            return obj.special_service.apartment_number  # adjust field name
        return None
