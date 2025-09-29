from django.contrib import admin
from .models import Subscription,PlanModel,SubscriptionHistory,InvoiceLineItem,InvoiceModel
# Register your models here.

admin.site.register(Subscription)
admin.site.register(PlanModel)
admin.site.register(InvoiceModel)
admin.site.register(InvoiceLineItem)
@admin.register(SubscriptionHistory)
class SubscribHistoryAdmin(admin.ModelAdmin):
    list_display=['id','created_at','action','amount']



