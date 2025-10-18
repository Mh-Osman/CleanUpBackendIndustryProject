from rest_framework import serializers
from .models import  Building, Apartment, Region
from users.models import CustomUser
from django.db import transaction
from plan.models import Subscription
from assign_task_employee.models import SpecialServicesModel
from rating.models import RatingModel

class RegionSerializer(serializers.ModelSerializer):

    
    class Meta:
        model = Region
        fields = ['id', 'name']
        read_only_fields = ['id']

    

class ApartmentSerializerForBuilding(serializers.ModelSerializer):
    class Meta:
        model = Apartment
        fields = "__all__"


class BuildingSerializer(serializers.ModelSerializer):
    apartments = ApartmentSerializerForBuilding(many=True, read_only=True)
    region_name = serializers.SerializerMethodField(read_only=True)
  
    total_apartments = serializers.SerializerMethodField()
    active_apartments_in_building = serializers.SerializerMethodField()

  
    class Meta:
        model = Building
        fields = "__all__"  # Building এর ফিল্ডগুলো
        read_only_fields = ['id']


    def get_total_apartments(self, obj):
        return Apartment.objects.filter(building=obj).count()

    def get_active_apartments_in_building(self, obj):
        from_subscription = Subscription.objects.filter(status='active', apartment__building=obj).count()
        form_special_service = SpecialServicesModel.objects.filter(
            status__in=['pending','started'], apartment__building=obj
        ).count()
        total_active = from_subscription + form_special_service
        return total_active

    def get_region_name(self, obj):
        return obj.region.name if obj.region else None


class ApartmentSerializer(serializers.ModelSerializer):
    client = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.filter(user_type='client'), required=True, allow_null=True)
    building = BuildingSerializer(required=False)
    building_id = serializers.PrimaryKeyRelatedField(queryset=Building.objects.all(), source='building', write_only=True, required=False)

    class Meta:
        model = Apartment
        fields = "__all__"
        read_only_fields = ['id']
        UniqueTogether = ('building', 'client', 'apartment_number')
    
    
    # def validate(self, attrs):
    #     client = attrs.get("client")
    #     building_data = attrs.get("building") 
    #     building_instance = attrs.get("building_id")
    #     apartment_number = attrs.get("apartment_number")

    #     if isinstance(building_data, Building):

    #         if client and building_data:

    #             qs = Apartment.objects.filter(
    #             client=client, 
    #             building=building_data, 
    #             apartment_number=apartment_number, 
                
    #         )
            
    #         if self.instance:
    #                 qs = qs.exclude(pk=self.instance.pk)
                
    #         if qs.exists():
    #              raise serializers.ValidationError(
    #                 "This apartment is already assigned to this client in the same building."
    #             )
    #         print("hello")
    #         attrs["building"] = building_data
    #         return attrs
    #     if isinstance(building_data, dict):
    #         if building_data:
    #             building_instance, created = Building.objects.get_or_create(
    #                         name=building_data['name'],
    #                         type=building_data['type'],
    #                         city=building_data['city'],
    #                         location=building_data.get('location', "Unknown"),
    #                         defaults={
    #                             'latitude': building_data.get('latitude', 24.7136),
    #                             'longitude': building_data.get('longitude', 46.6753),
    #                         }
    #                     )
    #         building = building_instance
    #         if not building_instance:
    #             raise serializers.ValidationError("Either building or building_id is required")
            

    #         apartment_number = attrs.get("apartment_number")
    #         floor = attrs.get("floor")

    #         if client and building:
    #             if Apartment.objects.filter(
    #                 client=client, 
    #                 building=building, 
    #                 apartment_number=apartment_number, 
    #                 floor=floor
    #             ).exists():
    #                 raise serializers.ValidationError(
    #                     "This apartment is already assigned to this client in the same building."
    #                 )
    #         return attrs
   
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

    def update(self, instance, validated_data):
        # update client (only if provided)
        client = validated_data.get("client", instance.client)
        if client and client.user_type != "client":
            raise serializers.ValidationError("Invalid client ID")
        instance.client = client

        # update building (only if provided via building_id)
        if "building" in validated_data:
            instance.building = validated_data.get("building")

        # update other fields dynamically
        for attr, value in validated_data.items():
            if attr not in ["client", "building"]:  # already handled
                setattr(instance, attr, value)

        instance.save()
        return instance
            

class RegionDetailSerializer(serializers.ModelSerializer):
    buildings = BuildingSerializer(many=True, read_only=True)
    total_buildings = serializers.SerializerMethodField()
    total_apartments = serializers.SerializerMethodField()
    class Meta:
        model = Region
        fields = ['id', 'name', 'total_buildings', 'total_apartments', 'buildings']
        read_only_fields = ['id']

    
    def get_total_buildings(self, obj):
        return Building.objects.filter(region=obj).count()

    def get_total_apartments(self, obj):
        return Apartment.objects.filter(building__region=obj).count()