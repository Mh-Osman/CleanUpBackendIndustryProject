from django.contrib import admin
from .models import Building, Apartment

# class ApartmentAdmin(admin.ModelAdmin):
#     list_display = 
#     list_filter = ("building", "client")

# class BuildingAdmin(admin.ModelAdmin):
#     list_display = ("id",)

admin.site.register(Building)
admin.site.register(Apartment)
