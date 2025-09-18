from rest_framework import serializers
from .models import CustomUser, OTP

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ['id','name','email','phone','role','password','is_active']
        read_only_fields = ['id','is_active']

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            name = validated_data['name'],
            email=validated_data['email'],
            phone=validated_data['phone'],
            password=validated_data['password'],
            role=validated_data.get('role', 'client')
        )
        return user

class OTPVerifySerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.IntegerField()

class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.IntegerField()
    new_password = serializers.CharField(write_only=True)
