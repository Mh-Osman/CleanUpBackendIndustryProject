from django.db import models
from django.contrib.auth import get_user_model
from locations.models import Building,Apartment
from services_pakages.models import Category
from employeeProfiles.models import EmployeeProfile
from plan.models import PlanModel
from rest_framework.response import Response

User=get_user_model()

# Create your models here.

BILL_CYCLE=(
    ('Daily','Daily'),
    ('Monthly','Monthly'),
    ('yearly','Yearly'),
)



STATUS=(
    ('completed','completed'),
    ('started','started'),
    ('canceled','canceled'),
    ('pending','pending')
)


# feature or service create 

class FeatureModel(models.Model):
    name=models.CharField(max_length=100)
    price=models.CharField(max_length=10)

    def __str__(self):
        return f"id: {self.id} name: {self.name}  price : {self.price}"
# assigned task to the employee
class TaskAssignToEmployee(models.Model):
    name=models.CharField(max_length=100)
    # service_code=models.CharField(max_length=100)
    plan=models.ForeignKey(PlanModel,on_delete=models.CASCADE,related_name='tasks')
    description=models.TextField()
    category = models.ManyToManyField(Category)
    base_price=models.CharField(max_length=100)
    bill_cycle=models.CharField(choices=BILL_CYCLE,max_length=100)
    discount=models.CharField(max_length=10,blank=True,null=True)
    building=models.ForeignKey(Building,on_delete=models.CASCADE)
    apratment=models.ManyToManyField(Apartment)
    auto_renew_enable=models.BooleanField(default=True)
    worker=models.ForeignKey(User,on_delete=models.CASCADE)
    created_at=models.DateField(auto_now_add=True)
    package=models.ManyToManyField(FeatureModel)
    updated_at=models.DateField(auto_now=True)
    service_icon=models.ImageField(upload_to='./service/icon',blank=True,null=True)
    # status=models.BooleanField(default=True)
    tax_rate=models.CharField(null=True,blank=True)
    status=models.CharField(choices=STATUS,blank=True,null=True,default='pending')

    # class Meta:
    #     unique_together = ('employee', 'building','appartment')

    def __str__(self):
        return f'Task name {self.name} id is {self.id}'
    
    def clean_category(self):
     value = self.cleaned_data.get("category")
     if not value:
        raise models.ValidationError("Choose a valid category")
     return value




