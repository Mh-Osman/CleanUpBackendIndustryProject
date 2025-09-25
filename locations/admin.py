from django.contrib import admin

# Register your models here.
from .models import Region, Building, Apartment
class RegionAdmin(admin.ModelAdmin):
    list_display = ("id", "uuid", "name", "code", "input_code")

admin.site.register(Region, RegionAdmin)
admin.site.register(Building)   
admin.site.register(Apartment)