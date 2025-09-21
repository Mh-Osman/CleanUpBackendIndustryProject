from rest_framework import serializers
from .models import Service, Package, Feature, ServiceAssignment, Category


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description']
        read_only_fields = ['id']

class ServiceSerializer(serializers.ModelSerializer):