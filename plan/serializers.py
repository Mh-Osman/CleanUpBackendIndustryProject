from rest_framework import serializers
from .models import PlanModel

class PlanSerailzier(serializers.ModelSerializer):
    class Meta:
        model=PlanModel
        fields='__all__'
