from .models import Building,Apartment,Region
from rest_framework import serializers

class RegionSerializer(serializers.ModelSerializer):
    class Meta:
        model=Region
        fields='__all__'

class BuilingSerializer(serializers.ModelSerializer):
    
    class Meta:
        model=Building
        fields='__all__'



class ApartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model=Apartment
        fields='__all__'


