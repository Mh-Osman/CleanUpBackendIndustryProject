from rest_framework import serializers
from .models import LeaseFormModel

class LeaseFormSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaseFormModel
        fields = '__all__'

from .models import SupervisorFormModel 
class SupervisorFormSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupervisorFormModel
        fields = '__all__'