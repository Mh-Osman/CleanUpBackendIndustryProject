from rest_framework import serializers
from .models import  Building, Apartment
from users.models import CustomUser
from django.db import transaction

class BuildingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Building
        fields = "__all__"  # Building এর ফিল্ডগুলো
        read_only_fields = ['id']


class ApartmentSerializer(serializers.ModelSerializer):
    client = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.filter(user_type='client'), required=True, allow_null=True)
    building = BuildingSerializer(required=False)
    building_id = serializers.PrimaryKeyRelatedField(queryset=Building.objects.all(), source='building', write_only=True, required=False)
    class Meta:
        model = Apartment
        fields = "__all__"
        read_only_fields = ['id']
    
    
    def validate(self, attrs):
        client = attrs.get("client")
        building_data = attrs.get("building") 
        building_instance = attrs.get("building_id")
        apartment_number = attrs.get("apartment_number")

        if isinstance(building_data, Building):

            if client and building_data:

                if Apartment.objects.filter(
                client=client, 
                building=building_data, 
                apartment_number=apartment_number, 
                
            ).exists():
                 raise serializers.ValidationError(
                    "This apartment is already assigned to this client in the same building."
                )
            print("hello")
            attrs["building"] = building_data
            return attrs
        if isinstance(building_data, dict):
            if building_data:
                building_instance, created = Building.objects.get_or_create(
                            name=building_data['name'],
                            type=building_data['type'],
                            city=building_data['city'],
                            location=building_data.get('location', "Unknown"),
                            defaults={
                                'latitude': building_data.get('latitude', 24.7136),
                                'longitude': building_data.get('longitude', 46.6753),
                            }
                        )
            building = building_instance
            if not building_instance:
                raise serializers.ValidationError("Either building or building_id is required")
            

            apartment_number = attrs.get("apartment_number")
            floor = attrs.get("floor")

            if client and building:
                if Apartment.objects.filter(
                    client=client, 
                    building=building, 
                    apartment_number=apartment_number, 
                    floor=floor
                ).exists():
                    raise serializers.ValidationError(
                        "This apartment is already assigned to this client in the same building."
                    )
            return attrs
   
    def create(self, validated_data):
        try:
            with transaction.atomic():  # all or nothing
                # -------- validate client --------
                client = validated_data.get("client")
                if client and client.user_type != "client":
                     raise serializers.ValidationError("Invalid client ID")
                
                validated_data['client'] = client


                # -------- handle building --------
                building_data = validated_data.get("building", None)
                print("building_data", building_data)
               # building_instance = validated_data.pop("building_id", None)  # from building_id

                if building_data and isinstance(building_data , dict):
                    building_instance, created = Building.objects.get_or_create(
                        name=building_data['name'],
                        type=building_data['type'],
                        city=building_data['city'],
                        location=building_data.get('location', "Unknown"),
                        defaults={
                            'latitude': building_data.get('latitude', 24.7136),
                            'longitude': building_data.get('longitude', 46.6753),
                        }
                    )
                    validated_data['building'] = building_instance

                if not building_data:
                    raise serializers.ValidationError("Either building or building_id is required")

                
                # -------- create apartment --------
                apartment = Apartment.objects.create(**validated_data)

            return apartment

        except Exception as e:
            raise serializers.ValidationError(str(e))


         
            