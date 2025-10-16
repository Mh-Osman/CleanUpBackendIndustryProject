from django.shortcuts import render

# Create your views here.
from rest_framework import serializers
from .models import RatingModel
from users.models import CustomUser

class RatingSerializer(serializers.ModelSerializer):
    # client = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.filter(user_type='client'), required=False)
    employee = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.filter(user_type='employee'), required=True)
   # client = client_name = serializers.CharField(source='client.id', read_only=True)
    class Meta:
        model = RatingModel
        fields = ['id', 'employee', 'client', 'rating', 'review', 'created_at', 'updated_at']
