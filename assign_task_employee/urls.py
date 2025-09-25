from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TaskAssignmentEmployeeView

router = DefaultRouter()
router.register(r'task_assign_employee', TaskAssignmentEmployeeView)

urlpatterns = [
    path("",include(router.urls)),
]
