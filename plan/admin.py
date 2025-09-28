from django.contrib import admin
from .models import Subscription,PlanModel,SubscriptionHistory
# Register your models here.

admin.site.register(Subscription)
admin.site.register(PlanModel)
@admin.register(SubscriptionHistory)
class SubscribHistoryAdmin(admin.ModelAdmin):
    list_display=['id','created_at','action','amount']