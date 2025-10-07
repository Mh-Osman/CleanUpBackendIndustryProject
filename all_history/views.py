from django.shortcuts import render
from .serializers import HistoryTrackSerializer
from rest_framework.generics import ListAPIView
from auditlog.models import LogEntry
from rest_framework import permissions
# Create your views here.


class HistoryView(ListAPIView):
    queryset=LogEntry.objects.all().order_by('-timestamp')
    serializer_class=HistoryTrackSerializer
    permission_classs=[permissions.IsAdminUser]

