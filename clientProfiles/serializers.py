from rest_framework import serializers
from .models import CustomUser, ClientProfile

class ClientProfileSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model = ClientProfile
        fields = "__all__"   # ClientProfile এর ফিল্ডগুলো

class ClientSerializer(serializers.ModelSerializer):
    client_profile = ClientProfileSerializer(required=False)
    
    class Meta:
        model = CustomUser
        fields = ['id', 'name', 'email', 'phone', 'is_active', 'date_joined', 'client_profile']
        read_only_fields = ['id', 'date_joined']

    # ---------------- Create ----------------
    def create(self, validated_data):
        profile_data = validated_data.pop('client_profile', {})
        validated_data['user_type'] = 'client'
        validated_data['is_active'] = True  # new client active by default

        user = CustomUser.objects.create_user(**validated_data)

        # create profile
        ClientProfile.objects.create(user=user, **profile_data)

        return user

    # ---------------- Update / Patch ----------------
    def update(self, instance, validated_data):
        profile_data = validated_data.pop('client_profile', None)

        # update main user fields
        instance = super().update(instance, validated_data)

        # update or create profile
        if profile_data:
            profile, created = ClientProfile.objects.get_or_create(user=instance)
            # Use serializer for validation
            profile_serializer = ClientProfileSerializer(profile, data=profile_data, partial=True)
            profile_serializer.is_valid(raise_exception=True)
            profile_serializer.save()

        return instance

    # ---------------- Field validation ----------------
    def validate_email(self, value):
        user_id = self.instance.id if self.instance else None
        if CustomUser.objects.filter(email=value).exclude(id=user_id).exists():
            raise serializers.ValidationError("Email already in use.")
        return value

    def validate_phone(self, value):
        user_id = self.instance.id if self.instance else None
        if CustomUser.objects.filter(phone=value).exclude(id=user_id).exists():
            raise serializers.ValidationError("Phone number already in use.")
        return value
