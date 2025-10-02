from rest_framework import serializers
from .models import PlanModel,Subscription,SubscriptionHistory,InvoiceModel,InvoiceLineItem
from clientProfiles.serializers import ClientProfileSerializer
from locations.serializers import BuildingSerializer,ApartmentSerializer,RegionSerializer
from datetime import datetime
class PlanSerailzier(serializers.ModelSerializer):
    class Meta:
        model=PlanModel
        fields='__all__'


class SubscribeSerializer(serializers.ModelSerializer):
    user=ClientProfileSerializer(read_only=True)
    plan=PlanSerailzier(read_only=True)
    building=BuildingSerializer(read_only=True)
    apartment=ApartmentSerializer(read_only=True)
    region=RegionSerializer(read_only=True)
    remaining_days=serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model=Subscription
        fields=['user','plan','building','apartment','status','region','remaining_days']
    
    def get_remaining_days(self, obj):
        if obj.current_period_end:
            delta = obj.current_period_end.date() - datetime.now().date()
            return max(delta.days, 0)
        return 0



class SubscriptionHistorySerializer(serializers.ModelSerializer):
    class Meta:
        user=Subscription
        fields='__all__'




class SubscriptionStatusCountSerializer(serializers.Serializer):
    active = serializers.IntegerField()
    pending = serializers.IntegerField()
    inactive = serializers.IntegerField()
    expired = serializers.IntegerField()
    total_revinew_last_month=serializers.IntegerField()


from rest_framework import serializers

class InvoiceLineItemSerializer(serializers.ModelSerializer):
    total = serializers.ReadOnlyField()

    class Meta:
        model = InvoiceLineItem
        fields = ["description", "service", "quantity", "unit_price", "discount", "tax", "total"]


class InvoiceSerializer(serializers.ModelSerializer):
    line_items = InvoiceLineItemSerializer(many=True)
    total_amount = serializers.ReadOnlyField()
    date_issued = serializers.DateField(format="%m/%d/%Y", input_formats=["%m/%d/%Y"])
    due_date = serializers.DateField(format="%m/%d/%Y", input_formats=["%m/%d/%Y"])
    building_name=serializers.SerializerMethodField(read_only=True)
    apartment_name=serializers.SerializerMethodField(read_only=True)
    region_name=serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = InvoiceModel
        fields = [
            "invoice_id", "type", "date_issued", "due_date",
            "client",'building',"apartments", "plan", "vendor", 
            "vendor_invoice_file", "note", "file",
            "line_items", "total_amount","status","building_name","apartment_name","region_name",
        ]

    def create(self, validated_data):
        line_items_data = validated_data.pop("line_items")
        apartments_data = validated_data.pop("apartments", [])
        invoice = InvoiceModel.objects.create(**validated_data)
    
        if apartments_data:
         invoice.apartments.set(apartments_data)
        total = 0
        for item_data in line_items_data:
            item = InvoiceLineItem.objects.create(invoice=invoice, **item_data)
            total += item.total
        invoice.total_amount = total
        invoice.save(update_fields=["total_amount"])
        return invoice
    
    def get_building_name(self,obj):
        if obj.building:
            return obj.building.name
        return None
    
    def get_apartment_name(self,obj):
        name=[]
        if obj.apartments:
         for apr in obj.apartments.all():
            name.append(apr.apartment_number)
        return name
    
    def get_region_name(self,obj):
        if obj.building and obj.building.region:
          return obj.building.region.name