from django.db import models
import uuid
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from users.models import CustomUser
from auditlog.registry import auditlog
# <<<<<<< HEAD
# from django.forms import ValidationError


class Region(models.Model):
    """
    Represents a region/city in Saudi Arabia (like Riyadh, Jeddah).
    """
    id = models.AutoField(primary_key=True)  # integer id
    name = models.CharField(max_length=100)   # e.g. Riyadh
    
    class Meta:
        verbose_name = "Region"
        verbose_name_plural = "Regions"

   
    def __str__(self):
        return f"{self.name} ({self.id})"

auditlog.register(Region)
# =======
def validate_saudi_postcode(value):
    if not (1000 <= int(value) <= 9999):
        raise ValidationError(f"{value} is not a valid Saudi postcode.")
    return value
# >>>>>>> gani
class Building(models.Model):
    BUILDING_TYPES = [
        ("residential", "Residential"),
        ("commercial", "Commercial"),
    ]

    name = models.CharField(max_length=100)
    type = models.CharField(max_length=50, choices=BUILDING_TYPES)
    city = models.CharField(max_length=100)
    region = models.ForeignKey(Region, on_delete=models.CASCADE, related_name="buildings")
    location = models.CharField(max_length=255)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, default=24.7136)  # Riyadh default
    longitude = models.DecimalField(max_digits=9, decimal_places=6, default=46.6753)  # Riyadh default
    created_at = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.type}) in {self.city}"

auditlog.register(Building)

class Apartment(models.Model):
    client = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name="apartments")
    building = models.ForeignKey(Building, on_delete=models.CASCADE, related_name="apartments")
    apartment_number = models.CharField(max_length=50)
    floor = models.IntegerField()
    living_rooms = models.IntegerField()
    bathrooms = models.IntegerField()
    outdoor_area = models.BooleanField(default=False)
    postcode = models.CharField(max_length=5, validators=[validate_saudi_postcode])
    location = models.CharField(max_length=255)

    # class Meta:
    #     constraints = [
    #         models.UniqueConstraint(fields=['building', 'client', 'apartment_number'], name='unique_apartment_per_building')
    #     ]

    def __str__(self):
        return f"Apt {self.apartment_number}, {self.building.name}"

    def full_address(self):
        recipient_name = self.client.name if self.client else "Unknown Recipient"
        street_building = f"{self.building.location}, {self.building.name}"
        city = self.building.city
        postcode_line = f"{self.postcode} {city}"
        country = self.country
        return f"{recipient_name}\n{street_building}\n{city}\n{postcode_line}\n{country}"

auditlog.register(Apartment)