from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticated
from .models import LeaseFormModel, SupervisorFormModel
from .serializers import LeaseFormSerializer, SupervisorFormSerializer


# ✅ Custom Permission (inside same file)
class SupervisorPostAdminReadOnly(permissions.BasePermission):
    """
    Custom permission:
    - Admin can only GET (read-only)
    - Supervisor can only POST (create)
    - Others denied
    """

    # def has_permission(self, request, view):
    #     user = request.user

    #     # Not logged in → deny
    #     if not user or not user.is_authenticated:
    #         return False

    #     # Admins can only GET
    #     if user.is_staff or getattr(user, 'user_type', '') == 'admin':
    #         return request.method in permissions.SAFE_METHODS

    #     # Supervisors can only POST
    #     if getattr(user, 'user_type', '') == 'supervisor':
    #         return request.method in ['POST']
    #     # All others denied
    #     return False
    def has_object_permission(self, request, view, obj):
        print(request.user.id)
        return request.user==obj.supervisor or request.user.is_staff

class LeaseFormViewSet(viewsets.ModelViewSet):
    queryset = LeaseFormModel.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = LeaseFormSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = []  # Add any filter fields if needed
    search_fields = []  # Add any search fields if needed
    ordering_fields = []  # Add any ordering fields if needed


# ✅ SupervisorForm View
class SupervisorFormViewSet(viewsets.ModelViewSet):
    queryset = SupervisorFormModel.objects.all().order_by('-created_at')
    serializer_class = SupervisorFormSerializer
    permission_classes = [SupervisorPostAdminReadOnly]

    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['supervisor__name', 'employee__name', 'report_date', 'performance']
    search_fields = ['supervisor__name', 'employee__name', 'work_summary', 'supervisor_comments', 'issues_reported', 'performance']
    ordering_fields = ['report_date', 'last_updated', 'created_at']

from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
@api_view(['GET'])
def supervisor_form_list(request):
    user = request.user
    if not user.is_authenticated:
        return Response({"detail": "Authentication credentials were not provided."}, status=401)
    
    all_forms = SupervisorFormModel.objects.filter(supervisor=user)

    serializer = SupervisorFormSerializer(all_forms, many=True)
    return Response(serializer.data)