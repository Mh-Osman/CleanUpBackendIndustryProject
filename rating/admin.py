from django.contrib import admin

# Register your models here.
from .models import RatingModel
admin.site.register(RatingModel)