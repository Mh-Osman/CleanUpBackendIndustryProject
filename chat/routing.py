from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    # -----------------------------
    #  Group Chat WebSocket Route
    # -----------------------------
    re_path(
        r"ws/chat/group/(?P<group_name>\w+)/$",   # e.g. ws://localhost:8000/ws/chat/group/devs/
        consumers.GroupChatConsumer.as_asgi(),
        name="group_chat_socket"
    ),

    # -----------------------------
    # One-to-One Chat WebSocket Route
    # -----------------------------
    re_path(
        r"ws/chat/one-to-one/(?P<friend_username>\w+)/$",  # e.g. ws://localhost:8000/ws/chat/one-to-one/john/
        consumers.OneToOneChatConsumer.as_asgi(),
        name="one_to_one_chat_socket"
    ),
]
