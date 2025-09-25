from rest_framework import serializers
from .models import Region, Building, Apartment
from users.models import CustomUser
from clientProfiles.models import ClientProfile , ClientApartment

class RegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Region
        fields = ['id', 'name', 'code', 'input_code']
        read_only_fields = ['id']

class BuildingSerializer(serializers.ModelSerializer):
    region = RegionSerializer(read_only=True)  # response এ nested দেখাবে
    region_id = serializers.PrimaryKeyRelatedField(
        queryset=Region.objects.all(),
        write_only=True,
        required=False
    )

    class Meta:
        model = Building
        fields = ['id', 'name', 'code', 'location', 'region', 'region_id']
        read_only_fields = ['id']

    def create(self, validated_data):
        # check for region_id first
        region = None
        if 'region_id' in validated_data:
            region = validated_data.pop('region_id')
        elif 'region' in self.initial_data:
            region_data = validated_data.pop('region', None)
            if region_data and region_data.get('id'):
                region = Region.objects.get(id=region_data['id'])
            elif region_data:
                region, _ = Region.objects.get_or_create(**region_data)

        building = Building.objects.create(region=region, **validated_data)
        return building

    def update(self, instance, validated_data):
        # handle region update
        if 'region_id' in validated_data:
            instance.region = validated_data.pop('region_id')
        elif 'region' in self.initial_data:
            region_data = validated_data.pop('region', None)
            if region_data and region_data.get('id'):
                instance.region = Region.objects.get(id=region_data['id'])
            elif region_data:
                region, _ = Region.objects.get_or_create(**region_data)
                instance.region = region

        # update other fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
    


from rest_framework import serializers
from django.core.exceptions import ValidationError

class ApartmentSerializer(serializers.ModelSerializer):
    region = RegionSerializer(required=False)       # nested region input
    region_id = serializers.PrimaryKeyRelatedField(
        queryset=Region.objects.all(), write_only=True, required=False
    )
    building = BuildingSerializer(required=False)   # nested building input
    building_id = serializers.PrimaryKeyRelatedField(
        queryset=Building.objects.all(), write_only=True, required=False
    )

    class Meta:
        model = Apartment
        fields = [
            'id', 'client', 'name', 'uuid', 'code', 'input_code', 
            'location', 'floor', 'living_rooms', 'bedrooms', 'bathrooms',
            'kitchens', 'outdoor_area', 'building', 'building_id', 'region', 'region_id'
        ]
        read_only_fields = ['id']

    def create(self, validated_data):
        # ----------------------------
        # Handle client
        # ----------------------------
        client_data = validated_data.pop('client', None)
        if client_data:
            try:
                user = CustomUser.objects.get(id=client_data['id'])
                if user.user_type != 'client':
                    raise serializers.ValidationError("User is not a client.")
                client = ClientProfile.objects.get(user=user)
            except CustomUser.DoesNotExist:
                raise serializers.ValidationError("Client user does not exist.")
            except ClientProfile.DoesNotExist:
                raise serializers.ValidationError("Client profile not found.")
        else:
            raise serializers.ValidationError("Client data is required.")

        # ----------------------------
        # Handle region
        # ----------------------------
        region = None
        if 'region_id' in validated_data:
            region = validated_data.pop('region_id')
        elif 'region' in validated_data:
            region_data = validated_data.pop('region')
            if region_data.get('id'):
                region = Region.objects.get(id=region_data['id'])
            else:
                region, _ = Region.objects.get_or_create(**region_data)
        if not region:
            raise serializers.ValidationError("Region data is required.")

        # ----------------------------
        # Handle building
        # ----------------------------
        building = None
        if 'building_id' in validated_data:
            building = validated_data.pop('building_id')
        elif 'building' in validated_data:
            building_data = validated_data.pop('building')
            if building_data.get('id'):
                building = Building.objects.get(id=building_data['id'])
            else:
                building, _ = Building.objects.get_or_create(region=region, **building_data)
        if not building:
            raise serializers.ValidationError("Building data is required.")

        # ----------------------------
        # Create apartment
        # ----------------------------
        apartment = Apartment.objects.create(building=building, **validated_data)

        # ----------------------------
        # Create ClientApartment relation
        # ----------------------------
        ClientApartment.objects.create(
            client=user,
            region=region,
            building=building,
            apartment=apartment,
            location_details=apartment.location
        )

        return apartment

    # Optional: Add update() method if you need to handle nested updates
