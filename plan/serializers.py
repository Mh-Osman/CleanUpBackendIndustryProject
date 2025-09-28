from rest_framework import serializers
from .models import PlanModel,Subscription,SubscriptionHistory
from clientProfiles.serializers import ClientProfileSerializer
from locations.serializers import BuilingSerializer,ApartmentSerializer,RegionSerializer
from datetime import datetime
class PlanSerailzier(serializers.ModelSerializer):
    class Meta:
        model=PlanModel
        fields='__all__'


class SubscribeSerializer(serializers.ModelSerializer):
    user=ClientProfileSerializer(read_only=True)
    plan=PlanSerailzier(read_only=True)
    building=BuilingSerializer(read_only=True)
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