from django.db import models
import uuid


class Region(models.Model):
    """
    Represents a region/city in Saudi Arabia (like Riyadh, Jeddah).
    """
    id = models.AutoField(primary_key=True)  # integer id
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)  # extra uuid
    name = models.CharField(max_length=100)   # e.g. Riyadh
    code = models.CharField(max_length=50, unique=True)  # Short code, e.g. 'RYD'

    class Meta:
        verbose_name = "Region"
        verbose_name_plural = "Regions"

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
    region = models.ForeignKey(Region, on_delete=models.CASCADE, related_name="buildings")

    class Meta:
        verbose_name = "Building"
        verbose_name_plural = "Buildings"

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
    building = models.ForeignKey("Building", on_delete=models.CASCADE, related_name="apartments")

    class Meta:
        verbose_name = "Apartment"
        verbose_name_plural = "Apartments"

    def __str__(self):
        return f"{self.name} - {self.building.name}"

    def generate_code(self, client_code=None):
        """
        Generate unique apartment code: regionCode-buildingCode-clientCode
        """
        region_code = self.building.region.code
        building_code = self.building.code
        client_part = client_code or "XXX"
        return f"{region_code}-{building_code}-{client_part}"

    def save(self, *args, **kwargs):
        """
        Override save: auto-generate `code` if empty.
        Developer doesn’t need to call generate_code() manually.
        """
        if not self.code:
            client_code = kwargs.pop("client_code", None)
            self.code = self.generate_code(client_code=client_code)
        super().save(*args, **kwargs)
        