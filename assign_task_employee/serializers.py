from rest_framework import serializers
from .models import SpecialServicesModel
from locations.models import Building, Apartment
from locations.serializers import BuildingSerializer
from services_pakages.models import Category
from django.contrib.auth import get_user_model
from services_pakages.serializers import CategorySerializer
from .models import FeatureModel
from django.db.models import Sum
from decimal import Decimal

User = get_user_model()


class SpecialServicesModelSerializer(serializers.ModelSerializer):
    # category=CategorySerializer(many=True)
    # building=BuildingSerializer(read_only=True)
    building_name=serializers.CharField(source='building.name',read_only=True)
    region_name=serializers.CharField(source='building.region.name',read_only=True)
    active=serializers.SerializerMethodField(read_only=True)
    aprtment_number=serializers.SerializerMethodField(read_only=True)
    client_name=serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = SpecialServicesModel
        fields = [
            "id",
            "name",
            # "plan",
            "description",
            "category",
            "base_price",
            "bill_cycle",
            "discount",
            "tax_rate",
            "building",
            "auto_renew_enable",
            "worker",
            "created_at",
            "updated_at",
            "service_icon",
            "status",
            "apartment",
            # "package",
            # 'total_revenue',
            'active',
            'service_code',
            'region',
            'discounted_price',
            "building_name",
            "region_name",
            "active",
            "client_name",
            "aprtment_number",
            "created_at",
        ]
        read_only_fields = ["created_at", "updated_at","id","discounted_price"]

    def get_active(self,obj):
        return SpecialServicesModel.objects.filter(status='started').count()
    def get_total_revenue(self, obj):
        total = SpecialServicesModel.objects.filter(status='completed').aggregate(
            total_amount=Sum('discounted_price')
        )['total_amount']
        return total or 0
    
    def get_aprtment_number(self, obj):
        return [apartment.apartment_number for apartment in obj.apartment.all()]
    def get_client_name(self, obj):
        return [apartment.client.name if apartment.client else "unknown" for apartment in obj.apartment.all()]
    
   
    
    def validate(self, attrs):
      
        base_price = attrs.get('base_price', 0)
        discount = attrs.get('discount', 0)

        if base_price < 0:
            raise serializers.ValidationError({"base_price": "Base price must be non-negative."})
        if discount < 0:
            raise serializers.ValidationError({"discount": "Discount must be non-negative."})
        if discount > 100:
            attrs['discount'] = 100  
        return attrs
    
    def create(self, validated_data):
       
        base_price = Decimal(validated_data.get('base_price', 0))
        discount = Decimal(validated_data.get('discount', 0))
        apartments_data=validated_data.pop('apartment',[])
        # Calculate discounted price
        discounted_price = base_price - (base_price * discount / Decimal(100))
        validated_data['discounted_price'] = discounted_price

        # Create the model instance
        special_service = SpecialServicesModel.objects.create(**validated_data)
        if apartments_data:
          special_service.apartment.set(apartments_data)
        return special_service

class FeatureSerialzer(serializers.ModelSerializer):
    class Meta:
        model=FeatureModel
        fields='__all__'

class ServiceDetailsSerializer(serializers.ModelSerializer):
    category=CategorySerializer(read_only=True)
    building=BuildingSerializer(read_only=True)
    # package=FeatureSerialzer(read_only=True,many=True)
    active=serializers.SerializerMethodField(read_only=True)
    completed=serializers.SerializerMethodField(read_only=True)
    revenue=serializers.SerializerMethodField(read_only=True)
    pending=serializers.SerializerMethodField()
    total_booking=serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model=SpecialServicesModel
        fields = [
            "id",
            "name",
            # "plan",
            "description",
            "category",
            "base_price",
            "bill_cycle",
            "discount",
            "tax_rate",
            "building",
            "auto_renew_enable",
            "worker",
            "created_at",
            "updated_at",
            "service_icon",
            "status",
            "apartment",
            # "package",
            'status',
            'revenue',
            # 'package',
            'total_booking',
            'active',
            'completed',
            'pending',
            'service_code',
            'region',
            'discounted_price'
        ]

   

    def get_active(self,obj):
        return SpecialServicesModel.objects.filter(service_code=obj.service_code,status='started').count()
    def get_completed(self,obj):
        return SpecialServicesModel.objects.filter(service_code=obj.service_code,status='completed').count()
    def get_pending(self,obj):
        return SpecialServicesModel.objects.filter(service_code=obj.service_code,status='pending').count()
    def get_revenue(self, obj):
        
        total = SpecialServicesModel.objects.filter(service_code=obj.service_code, status='completed').aggregate(
            total_amount=Sum('discounted_price')
        )['total_amount']
        return total or 0

    def get_total_booking(self, obj):
        return SpecialServicesModel.objects.filter(service_code=obj.service_code).count()


class ServiceDetailsSerializerForEmployee(serializers.Serializer):
    total_tasks=serializers.IntegerField(default=0)
    pending=serializers.IntegerField(default=0)
    completed=serializers.IntegerField(default=0)
    in_progress=serializers.IntegerField(default=0)
    
# serializers.py
from rest_framework import serializers

class MonthlyTaskReportSerializer(serializers.Serializer):
    month = serializers.DateField()
    total_tasks = serializers.IntegerField()
    completed_tasks = serializers.IntegerField()
    pending_tasks = serializers.IntegerField()
    started_tasks = serializers.IntegerField()
    this_month_revenue=serializers.IntegerField()


from .models import RatingModelForService

class RatingForSpecialServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = RatingModelForService
        fields = '__all__'

    def validate(self, attrs):
        client = self.context['request'].user
        service= attrs.get('service')

   
        if not SpecialServicesModel.objects.filter(id=service.id, apartment__client=client).exists():
            raise serializers.ValidationError(
                "Hey brother! First buy the service, then try to review!"
            )

        
        if RatingModelForService.objects.filter(client=client, service=service).exists():
            raise serializers.ValidationError(
                "A user can only give one review for a service"
            )

        return attrs

    def create(self, validated_data):
        # Assign the current user as client
        validated_data['client'] = self.context['request'].user
        return super().create(validated_data)
