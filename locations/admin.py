from django.contrib import admin

# Register your models here.
from .models import Region, Building, Apartment
admin.site.register(Region)
admin.site.register(Building)   
admin.site.register(Apartment)