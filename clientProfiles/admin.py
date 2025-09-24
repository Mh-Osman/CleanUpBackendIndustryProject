from django.contrib import admin

# Register your models here.
from .models import ClientProfile
admin.site.register(ClientProfile)

from .models import ClientApartment
admin.site.register(ClientApartment)