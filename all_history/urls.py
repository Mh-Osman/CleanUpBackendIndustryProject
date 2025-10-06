from django.urls import path,include
from .views import HistoryView
urlpatterns = [
    path('list/',HistoryView.as_view()),
    ]
