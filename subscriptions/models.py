from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from services_pakages.models import Service, Package

class Subscription(models.Model):
    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,   # ✅ CustomUser handle করবে
        on_delete=models.CASCADE,
        related_name="subscriptions"
    )
    service = models.ForeignKey("Service", null=True, blank=True, on_delete=models.CASCADE)
    package = models.ForeignKey("Package", null=True, blank=True, on_delete=models.CASCADE)
    
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ("active", "Active"),
            ("paused", "Paused"),
            ("cancelled", "Cancelled")
        ],
        default="active"
    )

    def clean(self):
        # ✅ client যখন subscription তৈরি করবে,
        # তখন either service অথবা package থাকতে হবে (exclusive)
        if bool(self.service) == bool(self.package):
            raise ValidationError("একসাথে service & package দেওয়া যাবে না — একটিই লাগবে।")

    def __str__(self):
        if self.service:
            return f"{self.client} subscribed to service {self.service.name}"
        elif self.package:
            return f"{self.client} subscribed to package {self.package.name}"