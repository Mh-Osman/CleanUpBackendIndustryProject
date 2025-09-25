from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser

from .models import TaskAssignToEmployee
from .serializers import TaskAssignToEmployeeSerializer

class TaskAssignmentEmployeeView(viewsets.ModelViewSet):
    
    queryset = TaskAssignToEmployee.objects.all()
    serializer_class = TaskAssignToEmployeeSerializer
    # permission_classes = [IsAdminUser]  

    # Optional: filter by worker
    # def get_queryset(self):
    #     user = self.request.user
    #     return TaskAssignToEmployee.objects.filter(worker=user)
