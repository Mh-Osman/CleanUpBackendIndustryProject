# serializers.py

from rest_framework import serializers
from users.models import CustomUser
from .models import ClientProfile
from locations.models import Region, Building, Apartment

class ClientProfileSerializer(serializers.ModelSerializer):
    region = serializers.SlugRelatedField(
        queryset=Region.objects.all(), slug_field="name", required=False
    )
    building = serializers.SlugRelatedField(
        queryset=Building.objects.all(), slug_field="name", required=False
    )
    apartment = serializers.SlugRelatedField(
        queryset=Apartment.objects.all(), slug_field="number", required=False
    )

    class Meta:
        model = ClientProfile
      #  fields = ['region', 'building', 'apartment', 'avatar', 'location', 'birth_date', 'created_at', 'updated_at', 'last_login']
        fields = '__all__'

class ClientSerializer(serializers.ModelSerializer):
    client_profile = ClientProfileSerializer(required=False)
    location = serializers.CharField(source='client_profile.location', allow_blank=True, required=False)
    class Meta:
        model = CustomUser
        fields = ['id', 'name', 'email', 'phone', 'location','is_active', 'date_joined', 'client_profile']
        read_only_fields = ['id', 'date_joined']

    def create(self, validated_data):
        validated_data['is_active'] = True  # New clients are active by default
        location_data = validated_data.pop('location', None)
        profile_data = validated_data.pop("client_profile", None)
        if profile_data is None:
            profile_data = {}
        if location_data:
            profile_data['location'] = location_data
        validated_data['role'] = 'client'
        user = CustomUser.objects.create_user(**validated_data)

        # Add profile if data passed
        if profile_data:
            ClientProfile.objects.create(user=user, **profile_data)
        else:
            ClientProfile.objects.create(user=user)  # always ensure a profile exists
        return user

    def update(self, instance, validated_data):
        profile_data = validated_data.pop('client_profile', None)
        instance = super().update(instance, validated_data)

        if profile_data:
            ClientProfile.objects.update_or_create(
                user=instance, defaults=profile_data
            )
        return instance