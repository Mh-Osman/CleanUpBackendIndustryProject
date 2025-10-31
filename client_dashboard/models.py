from django.db import models
from users.models import CustomUser
# Create your models here
from plan.models import Subscription
from assign_task_employee.models import SpecialServicesModel


class ClientCheckoutForm(models.Model):
    CHOICES = (
        ("checkout", 'Checkout'),
        ("makeup", 'Makeup'),
        ("other", "Other"),
    )
    form_name = models.CharField(max_length=100)
    client = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True)
    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE, null=True, blank=True)
    special_service = models.ForeignKey(SpecialServicesModel, on_delete=models.CASCADE, null=True, blank=True)
    set_time = models.DateTimeField(auto_now_add=True)
    time_range = models.CharField(max_length=100)
    form_type = models.CharField(max_length=50, choices=CHOICES)
    description = models.TextField(blank=True, null=True)

