from django.contrib import admin
from .models import Building, Apartment, Region

# class ApartmentAdmin(admin.ModelAdmin):
#     list_display = 
#     list_filter = ("building", "client")

# class BuildingAdmin(admin.ModelAdmin):
#     list_display = ("id",)

# admin.site.register(Building)
@admin.register(Building)
class BuldingAdmin(admin.ModelAdmin):
    list_display=['id','name','region','city']
admin.site.register(Apartment)
admin.site.register(Region)
