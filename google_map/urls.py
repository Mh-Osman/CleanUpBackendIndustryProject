from django.urls import path
from . import views

urlpatterns = [
    path("map/<str:region_name>/", views.find_coordinates, name="get_coordinates"),
    
]