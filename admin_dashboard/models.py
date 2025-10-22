from django.db import models

# Create your models here.

class AdminProfileModel(models.Model):
    user = models.OneToOneField('users.CustomUser', on_delete=models.CASCADE, related_name='admin_profile')
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    location = models.TextField(blank=True, null=True)
    avatar = models.ImageField(upload_to='admin_avatars/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Admin Profile: {self.user.username}"