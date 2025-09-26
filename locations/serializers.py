from rest_framework import serializers
from .models import Region, Building, Apartment
from users.models import CustomUser
from clientProfiles.models import ClientProfile , ClientApartment
from django.db import transaction, IntegrityError

class RegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Region
        fields = ['id', 'name', 'code', 'input_code']
        read_only_fields = ['id']

    def validate(self, attrs):
        incoming_code = attrs.get("input_code")
        if incoming_code:
            qs_input = Region.objects.filter(input_code=incoming_code)
            if self.instance:
                qs_input = qs_input.exclude(pk=self.instance.pk)

            if qs_input.exists():
                raise serializers.ValidationError({
                    
                    "input_code": [f"⚠️ Region with input_code {incoming_code} already exists!"]
                })
            
        return attrs
    def create(self, validated_data):
        try:
            return super().create(validated_data)
        except ValidationError as e:
            raise serializers.ValidationError(e.message_dict)

    

class BuildingSerializer(serializers.ModelSerializer):
    region = RegionSerializer(required=False)  # nested input গ্রহণ করবে
    region_id = serializers.PrimaryKeyRelatedField(
        queryset=Region.objects.all(),
        write_only=True,
        required=False
    )
    
    class Meta:
        model = Building
        fields = ['id', 'name', 'code', 'location', 'region', 'region_id']
        read_only_fields = ['id']

    def get_region_from_data(self, validated_data):
        # region_id আগে চেক করুন
        if 'region_id' in validated_data:
            return validated_data.pop('region_id')
        # নেস্টেড region ডেটা চেক করুন
        region_data = validated_data.pop('region', None)
        if region_data:
            if region_data.get('id'):
                return Region.objects.get(id=region_data['id'])
            else:
                try:
                    # Region মডেলের save() থেকে ValidationError ধরার চেষ্টা
                    region = Region(**region_data)
                    region.save()
                    return region
                except ValidationError as e:
                    # Region থেকে ValidationError কে JSON আকারে serializer error এ রূপান্তর
                    
                    raise serializers.ValidationError(  {"region": ["Region with this  already exists! "
                           "Please select it from the dropdown instead of creating a new one."]})
        return None

    def create(self, validated_data):
        region = self.get_region_from_data(validated_data)
        if not region:
            raise serializers.ValidationError({"region": "Region data is required."})

        try:
            with transaction.atomic():
                building = Building.objects.create(region=region, **validated_data)
                return building
        except ValidationError as e:
            # Model থেকে আসা ValidationError preserve করা
            errors = e.message_dict
            for field in errors:
                errors[field] = [
                    f"{msg} Please select it from the dropdown instead of creating a new one."
                    for msg in errors[field]
                ]
            raise serializers.ValidationError(errors)
        except IntegrityError as e:
            # DB level uniqueness constraint fail হলে custom message
            raise serializers.ValidationError({
                "input_code": [
                    "Building with this input_code already exists! "
                    "Please select it from the dropdown instead of creating a new one."
                ]
            })

    def update(self, instance, validated_data):
        region = self.get_region_from_data(validated_data)
        if region:
            instance.region = region
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


from rest_framework import serializers
from django.core.exceptions import ValidationError

class ApartmentSerializer(serializers.ModelSerializer):
    client = serializers.DictField(write_only=True, required=False)  # client info from frontend
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
    

    def validate(self, attrs):
    
        # building = attrs.get("building")
        name = attrs.get("name")
        incoming_code = attrs.get("code")

        # if building and name:
        #     base_code = f"{building.region.code}{building.code}C{name}"
        #     # check duplicate
        #     if Apartment.objects.filter(code=base_code).exists():
        #         raise serializers.ValidationError({
        #             "code": [f"Apartment with code {base_code} already exists . "]
        #         })
            
        if incoming_code:
            qs_input = Apartment.objects.filter(input_code=incoming_code)
            if self.instance:
                qs_input = qs_input.exclude(pk=self.instance.pk)

            if qs_input.exists():
                
                raise serializers.ValidationError({
                    "input_code": [f"⚠️ Apartment with input_code '{incoming_code}' already exists!"]
                })
        return attrs
    
    

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
        try:
            if 'region_id' in validated_data:
                region = validated_data.pop('region_id')
            elif 'region' in validated_data:
                region_data = validated_data.pop('region')
                if region_data.get('id'):
                    region = Region.objects.get(id=region_data['id'])
                else:
                    region, _ = Region.objects.get_or_create(**region_data)
        except ValidationError as e:
            raise serializers.ValidationError({
                "region": e.message_dict if hasattr(e, "message_dict") else str(e)
            })
        except IntegrityError:
            raise serializers.ValidationError({
                "region": "⚠️ Region with this input_code already exists! Please select it from the dropdown."
            })

        if not region:
            raise serializers.ValidationError("Region data is required.")
        # ----------------------------
        # Handle building
        # ----------------------------
        building = None
        try:
            if 'building_id' in validated_data:
                building = validated_data.pop('building_id')
            elif 'building' in validated_data:
                building_data = validated_data.pop('building')
                if building_data.get('id'):
                    building = Building.objects.get(id=building_data['id'])
                else:
                    building, _ = Building.objects.get_or_create(region=region, **building_data)
        except ValidationError as e:
            raise serializers.ValidationError({
                "building": e.message_dict if hasattr(e, "message_dict") else str(e)
            })
        except IntegrityError:
            raise serializers.ValidationError({
                "building": "⚠️ Building with this input_code already exists! Please select it from the dropdown."
            })

        if not building:
            raise serializers.ValidationError("Building data is required.")
         # ----------------------------
        # Create apartment (inside transaction)
        # ----------------------------
        try:
            with transaction.atomic():
                apartment = Apartment.objects.create(building=building, **validated_data)

                # ClientApartment relation
                ClientApartment.objects.create(
                    client=user,
                    region=region,
                    building=building,
                    apartment=apartment,
                    location_details=apartment.location
                )
        except IntegrityError:
            raise serializers.ValidationError({
                "apartment": "⚠️ Apartment with this input_code already exists! Please select it instead of creating."
            })

        return apartment

 
class BuildingpageSerializer(serializers.ModelSerializer):
    active_apartments = serializers.SerializerMethodField()  # <- link to method

    class Meta:
        model = Building
        fields = ["id", "name", "code", "location", "active_apartments"]

    def get_active_apartments(self, obj):
        # Only apartments that have active clients
        active_apartments = Apartment.objects.filter(
            building=obj,
            client_apartments__is_primary=True  # marks active
        ).distinct()
        return ApartmentSerializer(active_apartments, many=True).data
    def get_inactive_apartments(self, obj):
        inactive = Apartment.objects.exclude(
            client_apartments__is_primary=True
        ).filter(building=obj).distinct()
        return ApartmentSerializer(inactive, many=True).data
        


