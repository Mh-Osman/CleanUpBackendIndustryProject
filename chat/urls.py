from django.urls import path
from .views import UploadFileViewFromGroup, UploadFileViewFromOneToOne, load_message

urlpatterns = [
    path('upload/', UploadFileViewFromGroup.as_view(), name='chat-upload'),
    path('upload/private/', UploadFileViewFromOneToOne.as_view(), name='chat-upload-private'),

    #  path for loading previous messages
    path('load-messages/', load_message, name='load-messages'),
]
