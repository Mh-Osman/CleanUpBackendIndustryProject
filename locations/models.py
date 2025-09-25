from django.db import models
import uuid
from django.core.exceptions import ValidationError

class Region(models.Model):
    """
    Represents a region/city in Saudi Arabia (like Riyadh, Jeddah).
    """
    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=50, unique=True)
    input_code = models.CharField(max_length=50, unique=True, null=True, blank=True)

    class Meta:
        verbose_name = "Region"
        verbose_name_plural = "Regions"

    def save(self, *args, **kwargs):
        creating = self._state.adding

        # First save to get ID if creating
        super().save(*args, **kwargs)

        # Auto-generate code
        new_code = f"R{self.name}{self.id}"

        # Avoid duplicates
        if Region.objects.filter(code=new_code).exclude(pk=self.pk).exists():
            raise ValidationError(f"⚠️ Region with code {new_code} already exists!")

        self.code = new_code

        # Set input_code if empty
        if not self.input_code:
            self.input_code = self.code

        # Save updated fields only if creating
        if creating:
            super().save(update_fields=["code", "input_code"])
        else:
            super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.code})"



class Building(models.Model):
    """
    Represents a building inside a region.
    """
    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    name = models.CharField(max_length=150)
    code = models.CharField(max_length=50, unique=True)
    input_code = models.CharField(max_length=50, unique=True, null=True, blank=True)
    region = models.ForeignKey(Region, on_delete=models.CASCADE, related_name="buildings")
    location = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        verbose_name = "Building"
        verbose_name_plural = "Buildings"

    def save(self, *args, **kwargs):
        creating = self._state.adding

        # First save to get ID if creating
        super().save(*args, **kwargs)

        # Auto-generate code
        new_code = f"{self.region.code}B{self.id}"

        # Avoid duplicates
        if Building.objects.filter(code=new_code).exclude(pk=self.pk).exists():
            raise ValidationError(f"⚠️ Building with code {new_code} already exists!")

        self.code = new_code

        # Set input_code if empty
        if not self.input_code:
            self.input_code = self.code

        # Save updated fields only if creating
        if creating:
            super().save(update_fields=["code", "input_code"])
        else:
            super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} - {self.region.name}"

from django.core.exceptions import ValidationError

class Apartment(models.Model):
    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=120, unique=True, db_index=True)
    input_code = models.CharField(max_length=50, unique=True, null=True, blank=True)
    building = models.ForeignKey("Building", on_delete=models.CASCADE, related_name="apartments")
    location = models.CharField(max_length=255, null=True, blank=True)
    floor = models.IntegerField(null=True, blank=True)
    living_rooms = models.IntegerField(default=1)
    bedrooms = models.IntegerField(default=1)
    bathrooms = models.IntegerField(default=1)
    kitchens = models.IntegerField(default=1)
    outdoor_area = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Apartment"
        verbose_name_plural = "Apartments"

    def __str__(self):
        return f"{self.name} - {self.building.name}"

    def save(self, *args, **kwargs):
        creating = self._state.adding  # check if new object

        # Save first to get ID (if creating)
        if creating:
            super().save(*args, **kwargs)

        # Auto-generate code
        new_code = f"{self.building.region.code}{self.building.code}C{self.name}"

        # Avoid duplicates
        if Apartment.objects.filter(code=new_code).exclude(pk=self.pk).exists():
            raise ValidationError(f"⚠️ Apartment with code {new_code} already exists!")

        self.code = new_code

        # Set input_code only if empty
        if not self.input_code:
            self.input_code = self.code

        # Save only updated fields if updating
        if creating:
            super().save(update_fields=['code', 'input_code'])
        else:
            super().save(*args, **kwargs)

