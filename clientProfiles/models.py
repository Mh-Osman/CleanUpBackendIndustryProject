from django.db import models
from locations.models import Region, Building, Apartment
import uuid
from django.utils import timezone
from users.models import CustomUser

class ClientProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name="client_profile")
    
    # Address Relation
    region = models.ForeignKey(Region, on_delete=models.SET_NULL, null=True, blank=True)
    building = models.ForeignKey(Building, on_delete=models.SET_NULL, null=True, blank=True)
    apartment = models.ForeignKey(Apartment, on_delete=models.SET_NULL, null=True, blank=True)

    # Extra profile info
    avatar = models.ImageField(upload_to="avatars/", null=True, blank=True)  # Profile Picture
    location = models.CharField(max_length=255, null=True, blank=True)        # Extra address info
    birth_date = models.DateField(null=True, blank=True)                      # Birthdate

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)  # create time auto set
    updated_at = models.DateTimeField(auto_now=True) 

    last_login = models.DateTimeField(null=True, blank=True)  # update when user logs in with signal

    def save(self, *args, **kwargs):
        # যদি client region/building বদলায় → তার apartment null হবে
        if self.pk:
            old = ClientProfile.objects.get(pk=self.pk)
            if old.region != self.region or old.building != self.building:
                self.apartment = None
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Client: {self.user.name}"

