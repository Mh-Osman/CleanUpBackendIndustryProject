from django.urls import path,include
from .views import DashboardRecentActivityView
urlpatterns = [
    path('list/',DashboardRecentActivityView.as_view()),
    ]
