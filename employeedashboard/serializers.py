from rest_framework import serializers
from .models import LeaseFormModel

class LeaseFormSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaseFormModel
        fields = '__all__'