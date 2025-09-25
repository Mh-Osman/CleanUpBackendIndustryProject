from django.db import models
import uuid

from django.forms import ValidationError


class Region(models.Model):
    """
    Represents a region/city in Saudi Arabia (like Riyadh, Jeddah).
    """
    id = models.AutoField(primary_key=True)  # integer id
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)  # extra uuid
    name = models.CharField(max_length=100)   # e.g. Riyadh
    code = models.CharField(max_length=50, unique=True)  # Short code, e.g. 'RYD'
    input_code = models.CharField(max_length=50, unique=True, null=True, blank=True)  # User input code (optional)
    class Meta:
        verbose_name = "Region"
        verbose_name_plural = "Regions"

    def save(self, *args, **kwargs):
        if self.id is None:
            super().save(*args, **kwargs)  # Save first to get an ID
        self.code = 'R'+self.name+str(self.id)  # Auto-generate code based on ID code by default
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.code})"


class Building(models.Model):
    """
    Represents a building inside a region.
    """
    id = models.AutoField(primary_key=True)  # integer id
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)  # extra uuid
    name = models.CharField(max_length=150)   # e.g. Building 101
    code = models.CharField(max_length=50, unique=True)  # Building code, e.g. RYD-B1
    input_code = models.CharField(max_length=50, unique=True, null=True, blank=True)  # User input code (optional)
    region = models.ForeignKey(Region, on_delete=models.CASCADE, related_name="buildings")
    location = models.CharField(max_length=255, null=True, blank=True)  # Extra location details
    class Meta:
        verbose_name = "Building"
        verbose_name_plural = "Buildings"
    def save(self, *args, **kwargs):
       
        if self.id is None:
            super().save(*args, **kwargs)  # Save first to get an ID   
        self.input_code = self.code 
        self.code = f"{self.region.code}B{self.id}"  # Auto-generate code if empty example Building code = RYD-B1
         
         # check duplicate manually (ignore self.pk if updating)
        super().save(*args, **kwargs)
    def __str__(self):
        return f"{self.name} - {self.region.name}"


class Apartment(models.Model):
    """
    Represents an individual apartment inside a building.
    Code is auto-generated as: regionCode-buildingCode-clientCode
    Example: RYD-B1-CL12
    """
    id = models.AutoField(primary_key=True)  # Integer PK
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)  # Safe future-proof ID
    name = models.CharField(max_length=100)  # e.g. Apt 302
    code = models.CharField(max_length=120, unique=True, db_index=True)  # indexed for fast search
    input_code = models.CharField(max_length=50, unique=True, null=True, blank=True)  # User input code (optional)
    building = models.ForeignKey("Building", on_delete=models.CASCADE, related_name="apartments")
    location = models.CharField(max_length=255, null=True, blank=True)  # Extra location details
    floor = models.IntegerField(null=True, blank=True)  # Optional floor number
    living_rooms = models.IntegerField(default=1)  # Number of living rooms
    bedrooms = models.IntegerField(default=1)      # Number of bedrooms
    bathrooms = models.IntegerField(default=1)     # Number of bathrooms
    kitchens = models.IntegerField(default=1)      # Number of kitchens
    outdoor_area = models.BooleanField(default=False)  # Has outdoor area or not
    created_at = models.DateTimeField(auto_now_add=True)  # Auto-set on creation
    updated_at = models.DateTimeField(auto_now=True)      # Auto-set on update
    class Meta:
        verbose_name = "Apartment"
        verbose_name_plural = "Apartments"

    def __str__(self):
        return f"{self.name} - {self.building.name}"


    def save(self, *args, **kwargs):
        
        # client-based code জেনারেট করতে গেলে ClientApartment ট্র্যাক করতে হবে
        # তাই আমরা প্রথম save এ শুধু Building/Region কোড রাখব
        if self.id is None:
            super().save(*args, **kwargs)  # Save first to get an ID 
        self.input_code = self.code   
        self.code = f"{self.building.region.code}{self.building.code}{'C'}{self.name}"
         # check duplicate manually (ignore self.pk if updating)
        if Apartment.objects.filter(code=self.code).exclude(pk=self.pk).exists():
            raise ValidationError(f"⚠️ Apartment with code {self.code} already exists!")
        super().save(*args, **kwargs)

