from django.contrib import admin

# Register your models here.
from .models import Service, Package,Feature,ServiceAssignment,Category

admin.site.register(Service)
admin.site.register(Package)
admin.site.register(Feature)
admin.site.register(ServiceAssignment)
admin.site.register(Category)