from rest_framework import viewsets

from .models import SpecialServicesModel
from .serializers import SpecialServicesModelSerializer,ServiceDetailsSerializer
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.generics import ListAPIView
from rest_framework import permissions,filters
from django.db.models import Q

class CustomWorkerPermission(permissions.BasePermission):
    """
    Allow workers to update only their own assigned tasks.
    """
    def has_object_permission(self, request, view, obj):
        return obj.worker == request.user

#this is 
class TaskAssignmentEmployeeView(viewsets.ModelViewSet):
    queryset = SpecialServicesModel.objects.all()
    serializer_class = SpecialServicesModelSerializer

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return [permissions.IsAuthenticated()]
        
        if self.request.method == 'PATCH':
            if self.request.user.is_staff:
                return [permissions.IsAdminUser()]
            return [CustomWorkerPermission()]
        return [permissions.IsAdminUser()]
    def get_queryset(self):
        if not self.request.user.is_staff:
            return self.queryset.filter(
                worker=self.request.user
            )
        return self.queryset

            
from django.db.models import OuterRef, Subquery

class ServiceDetailsListView(ListAPIView):
    permission_classes = [permissions.IsAdminUser]
    serializer_class = ServiceDetailsSerializer
    queryset = SpecialServicesModel.objects.all()
    filter_backends = [DjangoFilterBackend,filters.SearchFilter]
    filterset_fields = ['status','auto_renew_enable'] 
    search_fields = ['service_code', 'name', 'category','status','auto_renew_enable']
    def get_queryset(self):
        # Subquery to get latest ID per service_code
        latest_ids_subquery = SpecialServicesModel.objects.filter(
            service_code=OuterRef('service_code')
        ).order_by('-created_at').values('id')[:1]

        # Return queryset filtered by latest IDs
        return SpecialServicesModel.objects.filter(id__in=Subquery(latest_ids_subquery))


from .serializers import ServiceDetailsSerializerForEmployee
from rest_framework.views import APIView
from rest_framework.response import Response    
from django.utils import timezone
from django.db.models.functions import TruncMonth
from django.db.models import Count, Q
from datetime import timedelta
class ServiceDetailsShowForEmployeeView(APIView):
    permission_classes=[permissions.IsAuthenticated]
    def get(self, request, *args, **kwargs):
        user=request.user
        data={
            'total_tasks':SpecialServicesModel.objects.filter(worker=request.user).count(),
            'pending':SpecialServicesModel.objects.filter(worker=request.user,status='pending').count(),
            'completed':SpecialServicesModel.objects.filter(worker=request.user,status='completed').count(),
            'in_progress':SpecialServicesModel.objects.filter(worker=request.user,status='started').count(),
        }
        serializer=ServiceDetailsSerializerForEmployee(data)
        return Response(serializer.data)




from django.utils import timezone
from datetime import timedelta
from django.db.models import Count, Q,Sum
from django.db.models.functions import TruncMonth



class EmployeeTaskReportView(APIView):
    permission_classes=[permissions.IsAuthenticated]
    def get(self, request, worker_id):
        one_year_ago = timezone.now() - timedelta(days=365)
        report = (
            SpecialServicesModel.objects
            .filter(worker_id=worker_id, created_at__gte=one_year_ago)
            .annotate(month=TruncMonth('created_at'))
            .values('month')
            .annotate(
                total_tasks=Count('id'),
                completed_tasks=Count('id', filter=Q(status='completed')),
                pending_tasks=Count('id', filter=Q(status='pending')),
                started_tasks=Count('id', filter=Q(status='started')),
                this_month_revenue = Sum('discounted_price', filter=Q(status='completed'))
            )
            .order_by('month')
        )
        return Response(report)


class TotalServicesDetailsSerializreView(APIView):
    def get(self, request, *args, **kwargs):
          total_service = SpecialServicesModel.objects.values('service_code').distinct().count()
          active_booking=SpecialServicesModel.objects.filter(Q(status='pending')|Q(status='started')).count()
          total_revenue = SpecialServicesModel.objects.filter(status='completed').aggregate(
         total=Sum('discounted_price'))['total'] or 0
          
          return Response({
              'total_services':total_service,
              'active_booking':active_booking,
              'total_revenue':total_revenue,
          })
        