from rest_framework import viewsets, permissions
from .models import RatingModel
from .serializers import RatingSerializer

class RatingViewSet(viewsets.ModelViewSet):
    queryset = RatingModel.objects.all().order_by('-created_at')
    serializer_class = RatingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        # Automatically set client as logged-in user
        serializer.save(client=self.request.user)
