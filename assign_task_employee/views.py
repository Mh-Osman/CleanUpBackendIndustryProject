from rest_framework import viewsets

from .models import TaskAssignToEmployee
from .serializers import TaskAssignToEmployeeSerializer,ServiceDetailsSerializer
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.generics import ListAPIView
from rest_framework import permissions


class CustomWorkerPermission(permissions.BasePermission):
    """
    Allow workers to update only their own assigned tasks.
    """
    def has_object_permission(self, request, view, obj):
        return obj.worker == request.user


class TaskAssignmentEmployeeView(viewsets.ModelViewSet):
    queryset = TaskAssignToEmployee.objects.all()
    serializer_class = TaskAssignToEmployeeSerializer

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return [permissions.IsAuthenticated()]
        
        if self.request.method == 'PATCH':
            if self.request.user.is_staff:
                return [permissions.IsAdminUser()]
            return [CustomWorkerPermission()]
        return [permissions.IsAdminUser()]

            




class ServiceDetailsListView(ListAPIView):
    permission_classes = [permissions.IsAdminUser]
    serializer_class = ServiceDetailsSerializer
    queryset = TaskAssignToEmployee.objects.all()