from django.contrib import admin

# Register your models here.
from .models import EmployeeProfile
from .models import EmployeeSalary
admin.site.register(EmployeeProfile)
admin.site.register(EmployeeSalary)
