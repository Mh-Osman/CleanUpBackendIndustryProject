# chat/urls.py
from django.urls import path
from .views import UploadFileViewFromGroup, UploadFileViewFromOneToOne

urlpatterns = [
    path('upload/', UploadFileViewFromGroup.as_view(), name='chat-upload'),
    path('upload/private/', UploadFileViewFromOneToOne.as_view(), name='chat-upload-private'),
]
