from django.contrib import admin

# Register your models here.
from .models import CustomUser
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ("id", "email", "is_staff", "is_active", "is_superuser", "date_joined")
admin.site.register(CustomUser, CustomUserAdmin)
from .models import OTP
admin.site.register(OTP)