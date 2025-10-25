from django.urls import include, path
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'notifications', views.NotificationViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('mark_read_bulk/', views.mark_read_bulk, name='mark-read-bulk'),
    path('is_read_action/', views.Is_read_action, name='is-read-action'),
    path('notification_according_to_user/', views.notification_according_to_user, name='notification-according-to-user'),
]
