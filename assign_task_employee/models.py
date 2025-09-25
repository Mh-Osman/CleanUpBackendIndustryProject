from django.db import models
from django.contrib.auth import get_user_model
from locations.models import Building,Apartment
from services_pakages.models import Category
User=get_user_model()

# Create your models here.

BILL_CYCLE=(
    ('Daily','Daily'),
    ('Monthly','Monthly'),
)

#Dummy building
# class Building(models.Model):
#     name=models.CharField(max_length=100)

# # dummy apartment
# class Apartment(models.Model):
#     name=models.CharField(max_length=100)
#     building=models.ForeignKey(Building,on_delete=models.CASCADE)

STASTUS=(
    ('active','active'),
    ('pending','pending'),
    ('stop','stop'),
)

# assigned task to the employee
class TaskAssignToEmployee(models.Model):
    name=models.CharField(max_length=100)
    task_code=models.CharField(max_length=100)
    description=models.TextField()
    category = models.ManyToManyField(Category,blank=True,null=True)
    base_price=models.CharField(max_length=100)
    bill_cycle=models.CharField(choices=BILL_CYCLE,max_length=100)
    discount=models.CharField(max_length=10,blank=True,null=True)
    tax_rate=models.CharField(max_length=10,blank=True,null=True)
    building=models.ForeignKey(Building,on_delete=models.SET_NULL,null=True)
    apratment=models.ManyToManyField(Apartment,blank=True,null=True)
    auto_renew_enable=models.BooleanField(default=True)
    worker=models.ForeignKey(User,on_delete=models.SET_NULL,null=True)
    created_at=models.DateField(auto_now_add=True)
    updated_at=models.DateField(auto_now=True)
    service_icon=models.ImageField(upload_to='./service/icon',blank=True,null=True)
    status=models.BooleanField(default=True)

    # class Meta:
    #     unique_together = ('employee', 'building','appartment')

    def __str__(self):
        return f'Task name {self.name} and task_code is {self.task_code}'