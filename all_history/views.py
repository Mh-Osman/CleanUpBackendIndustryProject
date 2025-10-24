from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from auditlog.models import LogEntry
from .serializers import HistoryTrackSerializer


class DashboardRecentActivityView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request, *args, **kwargs):
            

            logs = (
                LogEntry.objects.select_related("actor", "content_type")
                .order_by("-timestamp")[:20]  # ✅ Use timestamp, not action_time
            )

            serializer = HistoryTrackSerializer(logs, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
    # def post(self, request, *args, **kwargs):
          
        

