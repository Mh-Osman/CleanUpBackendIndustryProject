from rest_framework import serializers
from .models import PlanModel,Subscription,SubscriptionHistory,InvoiceModel,InvoiceLineItem,ServiceLineItem
from clientProfiles.serializers import ClientProfileSerializer
from locations.serializers import BuildingSerializer,ApartmentSerializer,RegionSerializer
from locations.models import Building,Apartment,Region
from datetime import datetime,timedelta
from rest_framework.response import Response



#salah uddin
class ServiceLineItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceLineItem
        fields = ["id","name","description","quantity","unit_price"]

class PlanSerailzier(serializers.ModelSerializer):
    #salah uddin
    service_line_items=ServiceLineItemSerializer(many=True)
    # total=serializers.ReadOnlyField()
    class Meta:
        model=PlanModel
        fields=["id","name","plan_code","interval","amount","description","is_active","category","discount","auto_renewal","service_line_items"]
        read_only_fields=["created_at","updated_at"]
    def validate(self, attrs):
      amount = attrs.get('amount')
      discount = attrs.get('discount')
      if amount is not None and amount < 0:
        raise serializers.ValidationError({"amount": "Amount must be positive"})
      if discount is not None and discount < 0:
        raise serializers.ValidationError({"discount": "Discount must be positive"})
      return attrs

    #salah uddin
    def create(self, validated_data):
        amount = validated_data.get('amount', 0)
        discount = validated_data.get('discount', 0)
        if amount>0 and discount>0:
            validated_data['amount'] = amount - (amount * discount / 100.00)
    
        service_line_items=validated_data.pop('service_line_items',[])
        plan = PlanModel.objects.create(**validated_data)
        if service_line_items:
            for pkg in service_line_items:
                ServiceLineItem.objects.create(plan=plan,**pkg)

  
        return plan
    def update(self, instance, validated_data):
        service_line_items = validated_data.pop('service_line_items', None)

        # Update plan fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Handle nested service line items update
        if service_line_items is not None:
            # Delete old items
            instance.service_line_items.all().delete()

            # Recreate new ones
            for item in service_line_items:
                ServiceLineItem.objects.create(plan=instance, **item)

        return instance
            

 

class CalculationsForInvoice(serializers.Serializer):
    total=serializers.IntegerField()
    sales=serializers.IntegerField()
    expense=serializers.IntegerField()
    total_invoice=serializers.IntegerField()




from rest_framework import serializers
from .models import Subscription, PlanModel, Building, Apartment, Region

class SubscriptionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = [
            "user",
            "plan",
            "building",
            "apartment",
            "region",
            "status",
            "start_date",
            "current_period_end",
            "pause_until",
            "payment", #salah uddin 
            "employee" #salah uddin 
            # "service",
            # "supervisor",
        ]
        read_only_fields = ["created_at", "updated_at"]
        

    def validate(self, attrs):
      user = attrs.get('user')
      plan = attrs.get('plan')
      building = attrs.get('building')
      apartment = attrs.get('apartment')
      region = attrs.get('region')
      start_date = attrs.get('start_date')
      current_period_end = attrs.get('current_period_end')
      status = attrs.get("status")

    # Only enforce required fields during creation
      if self.instance is None:
        required_fields = [user, plan, building, apartment, region, start_date, status]
        if not all(required_fields):
            raise serializers.ValidationError(
                "All fields (user, plan, building, apartment, region, start_date, current_period_end, status) are required."
            )

        # Prevent duplicate active/pending subscriptions
        subscription = Subscription.objects.filter(
            user=user,
            plan=plan,
            building=building,
            region=region,
            apartment=apartment,
            status__in=['active', 'paused', 'past_due']
        ).first()

        if subscription:
            if subscription.status == 'active':
                raise serializers.ValidationError("You already have this plan active on this apartment.")
            elif subscription.status == 'paused':
                raise serializers.ValidationError("This plan is paused — use resume to activate it.")
            elif subscription.status == 'past_due':
                raise serializers.ValidationError("Your subscription is past due — update it first.")
    
      # For PATCH, no strict required field check
      return attrs


         
from users.serializers import UserSerializer

class SubscribeSerializerDetails(serializers.ModelSerializer):
    user=UserSerializer(read_only=True)
    plan=PlanSerailzier(read_only=True)
    building=BuildingSerializer(read_only=True)
    apartment=ApartmentSerializer(read_only=True)
    region=RegionSerializer(read_only=True)
    remaining_days=serializers.SerializerMethodField(read_only=True)
    
    
    class Meta:
        model=Subscription
        fields=['id','user','plan','building','apartment','status','region','remaining_days','payment','employee','canceled_at','paused_at','start_date','current_period_end','created_at','updated_at']
        read_only_fields=['canceled_at','paused_at','created_at','updated_at']
        
    def get_remaining_days(self, obj):
        if obj.current_period_end:
            delta = obj.current_period_end- obj.start_date
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

from rest_framework import serializers
from .models import InvoiceLineItem

class InvoiceLineItemSerializer(serializers.ModelSerializer):
    total = serializers.ReadOnlyField()

    class Meta:
        model = InvoiceLineItem
        fields = [
            "description",
            "service_name",
            "quantity",
            "unit_price",
            "discount",
            "tax",
            "total",
            'sub_total',
        ]

    def validate(self, attrs):
        unit_price = attrs.get("unit_price", 0)
        discount = attrs.get("discount", 0)
        tax = attrs.get("tax", 0)
        quantity = attrs.get("quantity", 1)

        # Validation rules
        if unit_price < 0:
            raise serializers.ValidationError({"unit_price": "Unit price must be positive."})
        if discount < 0:
            raise serializers.ValidationError({"discount": "Discount must be positive."})
        if tax < 0:
            raise serializers.ValidationError({"tax": "Tax must be positive."})
        if quantity <= 0:
            raise serializers.ValidationError({"quantity": "Quantity must be at least 1."})
        if discount > 100:
            raise serializers.ValidationError({"discount": "Discount cannot exceed 100%."})
        if tax > 100:
            raise serializers.ValidationError({"tax": "Tax cannot exceed 100%."})

        return attrs

    

    


class InvoiceSerializer(serializers.ModelSerializer):
    line_items = InvoiceLineItemSerializer(many=True)
    total_amount = serializers.ReadOnlyField()
    date_issued = serializers.DateField(format="%m/%d/%Y", input_formats=["%m/%d/%Y"])
    due_date = serializers.DateField(format="%m/%d/%Y", input_formats=["%m/%d/%Y"])
    building_name=serializers.SerializerMethodField(read_only=True)
    apartment_name=serializers.SerializerMethodField(read_only=True)
    region_name=serializers.SerializerMethodField(read_only=True)
    client_name=serializers.SerializerMethodField(read_only=True)
    plan_name=serializers.SerializerMethodField(read_only=True)
    tax_percentage=serializers.SerializerMethodField(read_only=True)
    # sub_total=serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = InvoiceModel
        fields = [
            "id","invoice_id", "type", "date_issued", "due_date",
            "client",'building',"apartments", "plan", "vendor",'vendor_name',
            "vendor_invoice_file", "note", "file",
            "line_items", "total_amount","status","building_name","apartment_name","region_name","client_name","plan_name","tax_percentage",'sub_total'
        ]

    def create(self, validated_data):
        line_items_data = validated_data.pop("line_items")
        apartments_data = validated_data.pop("apartments",[])
        invoice = InvoiceModel.objects.create(**validated_data)
    
        if apartments_data:
         invoice.apartments.set(apartments_data)
        total = 0
        subtotal=0
        if not line_items_data:
            total=invoice.plan.amount
            subtotal=invoice.plan.amount
        for item_data in line_items_data:
            item = InvoiceLineItem.objects.create(invoice=invoice, **item_data)
            total += item.total
            subtotal+=item.sub_total
        invoice.total_amount = total
        invoice.sub_total=subtotal
        invoice.save(update_fields=["total_amount","sub_total"])
        

        return invoice
    
    def get_building_name(self,obj):
        if obj.building:
            return obj.building.name
        return None
    def get_tax_percentage(self,obj):
       return obj.total_tax_percentage
    # def get_sub_total(self,obj):
    #    sub_total=obj.total_amount
    #    return float(obj.total_amount)-obj.total_tax_percentage
    def get_apartment_name(self,obj):
        name=[]
        if obj.apartments:
         for apr in obj.apartments.all():
            name.append(apr.apartment_number)
        return name
    
    def get_region_name(self,obj):
        if obj.building and obj.building.region:
          return obj.building.region.name
    
    def get_client_name(self,obj):
       return obj.client.name if obj.client else None
    
    def get_plan_name(self,obj):
       return obj.plan.name if obj.plan else None