from django.urls import path
from .views import AdminReportAnalysisView
urlpatterns = [
    path('',AdminReportAnalysisView.as_view()),
]
