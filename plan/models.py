from django.db import models
from django.conf import settings
from locations.models import Apartment,Building,Region
from datetime import datetime,timezone
from clientProfiles.models import ClientProfile
from django.contrib.auth import get_user_model
User=get_user_model()
# Create your models here.

class PlanModel(models.Model):
    name = models.CharField(max_length=100)  
    plan_code = models.CharField(max_length=50, unique=True)  
    stripe_price_id = models.CharField(max_length=100) 
    amount = models.IntegerField(help_text="Price in cents")  
    interval = models.CharField(
        max_length=20,
        choices=(("month", "Monthly"), ("year", "Yearly")),
        default="month"
    )
    description = models.TextField(blank=True, null=True)  
    is_active = models.BooleanField(default=True)  

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

    user = models.ForeignKey(User, on_delete=models.CASCADE,null=True,blank=True)
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







class SubscriptionHistory(models.Model):
    subscription = models.ForeignKey(Subscription, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=50)  
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True) 
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'{self.action} {self.amount} {self.created_at}'

    # def clean(self):
    #     if self.subscription:
    #         if self.subscription.plan:
    #             amount=self.subscription.plan.amount
    
