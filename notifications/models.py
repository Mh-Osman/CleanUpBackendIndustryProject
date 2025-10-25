from django.db import models
from users.models import CustomUser
class Notification(models.Model):
    title = models.CharField(max_length=255)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    for_user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='notifications', null=True, blank=True)
    for_admin = models.BooleanField(default=False)
    for_all = models.BooleanField(default=False)

    def __str__(self):
        return self.title
    
