from django.contrib import admin
from .models import SpecialServicesModel,FeatureModel,RatingModelForService
# Register your models here.

admin.site.register(SpecialServicesModel)
admin.site.register(FeatureModel)

admin.site.register(RatingModelForService)

