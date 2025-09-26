from django.contrib import admin

# Register your models here.
from .models import Region, Building, Apartment
class RegionAdmin(admin.ModelAdmin):
    list_display = ("id", "uuid", "name", "code", "input_code")

class BuildingAdmin(admin.ModelAdmin):
    list_display = ("id", "uuid", "name", "code", "input_code", "region", "location")

class ApartmentAdmin(admin.ModelAdmin):
    list_display = ("id", "uuid", "name", "code", "building", "region")
admin.site.register(Region, RegionAdmin)
admin.site.register(Building, BuildingAdmin)   
admin.site.register(Apartment)