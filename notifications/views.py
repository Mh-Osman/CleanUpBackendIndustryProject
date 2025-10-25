from urllib import response
from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets
from .models import Notification
from .serializers import NotificationSerializer
from rest_framework import response
from rest_framework import status
class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer


from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def Is_read_action(request):
    
    id = request.data.get('id')
    notification = Notification.objects.get(id=id)
    notification.is_read = True
    notification.save()
    return response.Response({"message": "Notification marked as read."})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_read_bulk(request):
    if request.user.is_staff:
        obj = Notification.objects.filter(for_admin=True)
    else:   
        obj = Notification.objects.filter(for_user=request.user)
    
    obj.update(is_read=True)
    return response.Response({"message": "Notifications marked as read."})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def notification_according_to_user(request):
    notifications_all = Notification.objects.filter(for_all= True)
    if request.user.is_staff:
        notifications = Notification.objects.filter(for_admin=True )
        notifications = notifications | notifications_all
    else:
        notifications = Notification.objects.filter(for_user=request.user, for_all= True)
        notifications = notifications | notifications_all
    
    serializer = NotificationSerializer(notifications, many=True)
    return response.Response(serializer.data, status=status.HTTP_200_OK)