from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status,parsers
from auditlog.models import LogEntry
from .serializers import HistoryTrackSerializer
from rest_framework.pagination import PageNumberPagination


class DashboardRecentActivityView(APIView):
    permission_classes = [permissions.IsAdminUser]
    

    def get(self, request, *args, **kwargs):
            

            logs = (
                LogEntry.objects.select_related("actor", "content_type")
                .order_by("-timestamp")  # ✅ Use timestamp, not action_time
            )
            paginator = PageNumberPagination()
            paginator.page_size = 10   # change number as you want (e.g., 5, 20)
            result_page = paginator.paginate_queryset(logs, request)
            serializer = HistoryTrackSerializer(logs, many=True)
            return paginator.get_paginated_response(serializer.data)
    # def post(self, request, *args, **kwargs):
          
        

