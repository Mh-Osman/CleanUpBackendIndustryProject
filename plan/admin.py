from django.contrib import admin
from .models import Subscription,PlanModel
# Register your models here.

admin.site.register(Subscription)
admin.site.register(PlanModel)