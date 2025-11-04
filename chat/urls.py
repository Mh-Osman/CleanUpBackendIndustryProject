from django.urls import path
from .views import UploadFileViewFromGroup, UploadFileViewFromOneToOne, load_message,load_message_from_all_chat,connected_users

urlpatterns = [
    path('upload/', UploadFileViewFromGroup.as_view(), name='chat-upload'),
    path('upload/private/', UploadFileViewFromOneToOne.as_view(), name='chat-upload-private'),

    #  path for loading previous messages
    path('load-messages/', load_message, name='load-messages'),
    path('load-messages/chats/', load_message_from_all_chat, name='load-messages-all-chats'),
    path('connected-users/', connected_users, name='connected-users'),
]
