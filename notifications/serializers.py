from rest_framework import serializers
from django.contrib.auth import get_user_model
from notifications.models import Notification
# Adjust this import to match your actual model location/name
from .models import Notification

User = get_user_model()

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = "__all__"

