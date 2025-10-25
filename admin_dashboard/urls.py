from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AdminUserViewSet
from . import views
router = DefaultRouter()
router.register('profile', AdminUserViewSet, basename='admin-user')

urlpatterns = [
    path('', views.DashBoardTopView.as_view(), name='dashboard-top'),
    path('admin/', include(router.urls)),  # <-- include the router URLs
]
