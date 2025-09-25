
from django.db import models

from django.db import models
from django.conf import settings
from django.utils.timezone import now


class Category(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    def __str__(self):
        return self.name

class Service(models.Model):
    BILLING_CHOICES = [
        ("daily", "Daily"),
        ("weekly", "Weekly"),
        ("monthly", "Monthly"),
        ("yearly", "Yearly"),
    ]
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="services")
    billing_cycle = models.CharField(max_length=10, choices=BILLING_CHOICES, default="monthly")

    def __str__(self):
        return self.name

class Package(models.Model):
    name = models.CharField(max_length=255)
    services = models.ManyToManyField(Service, related_name="included_in_packages")
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)

class Feature(models.Model):
    service = models.ForeignKey("Service", on_delete=models.CASCADE, related_name="features")
    title = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.title} ({self.service.name})"


class ServiceAssignment(models.Model):
    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="service_assignments",
        limit_choices_to={'user_type': 'client'}
    )
    apartment = models.ForeignKey("locations.Apartment", on_delete=models.CASCADE, related_name="service_assignments")
    service = models.ForeignKey("Service", null=True, blank=True, on_delete=models.CASCADE)
    package = models.ForeignKey("Package", null=True, blank=True, on_delete=models.CASCADE)

    # 👇 apartment থেকে active employees set হবে
    employees = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="service_works",
        limit_choices_to={'user_type': 'employee'}
    )

    assigned_date = models.DateTimeField(auto_now_add=True)
    completed_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.client.username} → {self.service or self.package} at {self.apartment.code}"