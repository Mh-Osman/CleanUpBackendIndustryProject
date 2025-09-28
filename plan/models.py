from django.db import models
from django.conf import settings
from locations.models import Apartment,Building,Region
from datetime import datetime,timezone
# Create your models here.

class PlanModel(models.Model):
    name = models.CharField(max_length=100)  # Human readable name, যেমন "Basic Plan"
    plan_code = models.CharField(max_length=50, unique=True)  # Internal code / slug
    stripe_price_id = models.CharField(max_length=100)  # Stripe Price ID
    amount = models.IntegerField(help_text="Price in cents")  # Stripe smallest currency unit
    interval = models.CharField(
        max_length=20,
        choices=(("month", "Monthly"), ("year", "Yearly")),
        default="month"
    )
    description = models.TextField(blank=True, null=True)  # Optional plan description
    is_active = models.BooleanField(default=True)  # Future: to enable/disable plan in frontend

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f'{self.plan_code} - {self.name}'





class Subscription(models.Model):
    STATUS_CHOICES = (
        ("active","Active"),
        ("inactive","Inactive"),
        ("paused","Paused"),
        ("canceled","Canceled"),
        ("past_due","past_due"),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    plan = models.ForeignKey("PlanModel", on_delete=models.SET_NULL, null=True)
    building = models.ForeignKey(Building, on_delete=models.SET_NULL, null=True, blank=True)
    apartment = models.ForeignKey(Apartment, on_delete=models.SET_NULL, null=True, blank=True)
    region = models.ForeignKey(Region, on_delete=models.SET_NULL, null=True, blank=True)
    stripe_customer_id = models.CharField(max_length=100, blank=True, null=True)
    stripe_subscription_id = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="inactive")
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    current_period_end = models.DateTimeField(null=True, blank=True)
    pause_until = models.DateTimeField(null=True, blank=True)  # for paused subscriptions
    created_at = models.DateTimeField(auto_now_add=True,null=True,blank=True)
    updated_at = models.DateTimeField(auto_now=True,null=True,blank=True)



    def __str__(self):
        return f"{self.user} - {self.plan} ({self.status}) id is {self.id}"

