from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TaskAssignmentEmployeeView,ServiceDetailsListView,ServiceDetailsShowForEmployeeView,EmployeeTaskReportView,TotalServicesDetailsSerializreView,RatingForeSpecialServiceView
router = DefaultRouter()
router.register(f'task_assign_employee', TaskAssignmentEmployeeView)

urlpatterns = [
    path("",include(router.urls)),
    path("services/details/",ServiceDetailsListView.as_view()),
    path("service-detail-for-employee/",ServiceDetailsShowForEmployeeView.as_view()),
    path('report/employee/<int:worker_id>/', EmployeeTaskReportView.as_view(), name='employee-task-report'),
    path('total-service-details/',TotalServicesDetailsSerializreView.as_view()),
    path('service/rating/',RatingForeSpecialServiceView.as_view()),
]
