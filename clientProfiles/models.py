from django.db import models
from django.forms import ValidationError
#from locations.models import Region, Building, Apartment
import uuid
from django.utils import timezone
from users.models import CustomUser

class ClientProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name="client_profile" , limit_choices_to={'user_type': 'client'})
    
    # Extra profile info
    avatar = models.ImageField(upload_to="avatars/", null=True, blank=True)  # Profile Picture
    location = models.CharField(max_length=255, null=True, blank=True)        # Extra address info
    birth_date = models.DateField(null=True, blank=True)                      # Birthdate

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)  # create time auto set
    updated_at = models.DateTimeField(auto_now=True) 


    
  
    def __str__(self):
        return f"Client: {self.user.email}"
    
class ClientPhone(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="phones" , limit_choices_to={'user_type': 'client'})
    phone_number = models.CharField(max_length=15)

    def __str__(self):
        return self.phone_number

# #represent mant to many relation between client and apartment with unique code
# class ClientApartment(models.Model):
#     # client = models.ForeignKey(ClientProfile, on_delete=models.CASCADE, related_name="client_apartments")
#     client = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="client_apartments" , limit_choices_to={'user_type': 'client'})
#     region = models.ForeignKey(Region, on_delete=models.CASCADE, related_name="client_regions")
#     building = models.ForeignKey(Building, on_delete=models.CASCADE, related_name="client_buildings")
#     apartment = models.ForeignKey(Apartment, on_delete=models.CASCADE, related_name="client_apartments")
#     location_details = models.CharField(max_length=255, null=True, blank=True)  # Extra location details
#     final_code = models.CharField(max_length=50, unique=True, blank=True)
#     is_primary = models.BooleanField(default=False)
#     active = models.BooleanField(default=True)

#     created_at = models.DateTimeField(auto_now_add=True)

#     def save(self, *args, **kwargs):
       
#         #region_code = self.apartment.building.region.code
#         building_code = self.apartment.building.code
#         #serially num based on client 
#         last_num = ClientApartment.objects.filter(client=self.client).count() + 1
#         num = str(last_num)
#         client_code = self.client.id
#         self.final_code = f"{building_code}{'C'}{client_code}-{num}" # Auto-generate code if empty example Building code = RYD-B1-C12-1
#         # if ClientApartment.objects.filter(client=self.client, apartment=self.apartment).exclude(pk=self.pk).exists():
#         #     raise ValidationError("❌ This apartment is already assigned to this client!")  #vvi
#         super().save(*args, **kwargs)

#     def __str__(self):
#         return f"{self.final_code} ({self.client.name})"