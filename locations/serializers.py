from rest_framework import serializers
from .models import Region, Building, Apartment
from users.models import CustomUser

class RegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Region
        fields = ['id', 'name', 'code']
        read_only_fields = ['id']

class BuildingSerializer(serializers.ModelSerializer):
    region = RegionSerializer()
    class Meta:
        model = Building
        fields = ['id', 'name', 'code', 'region', 'region_id']
        read_only_fields = ['id']

class ApartmentSerializer(serializers.ModelSerializer):
    Region= RegionSerializer()
    building = BuildingSerializer()

    class Meta:
        model = Apartment
        fields = ['id', 'name','uuid' 'code','input_code','location', 'building', 'building_id','region_id','region']
        read_only_fields = ['id']

    def create(self, validated_data):
        building_data = validated_data.pop('building')
        region_data = building_data.pop('region')
        if region_data.get('id'):
            region = Region.objects.get(id=region_data['id'])
        else:
              region, _ = Region.objects.get_or_create(**region_data)

        if building_data.get('id'):
            building = Building.objects.get(id=building_data['id'])
        else:
            building, _ = Building.objects.get_or_create(region=region, **building_data)
            
        apartment = Apartment.objects.create(building=building, **validated_data)
        return apartment
    

