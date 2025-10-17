from django.db import models
from django.contrib.auth import get_user_model
from locations.models import Building,Apartment,Region
from services_pakages.models import Category
from employeeProfiles.models import EmployeeProfile
from plan.models import PlanModel
from rest_framework.response import Response
from auditlog.registry import auditlog
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


auditlog.register(FeatureModel)




   

# assigned task to the employee
class SpecialServicesModel(models.Model):
    name=models.CharField(max_length=100)
    # service_code=models.CharField(max_length=100)
    # plan=models.ForeignKey(PlanModel,on_delete=models.CASCADE,related_name='tasks')
    service_code=models.CharField(max_length=1000)
    description=models.TextField()
    category = models.ForeignKey(Category,on_delete=models.SET_NULL,null=True,blank=True)
    base_price=models.FloatField()
    bill_cycle=models.CharField(choices=BILL_CYCLE,max_length=100)
    discount=models.FloatField(blank=True,null=True,default=0)
    region=models.ForeignKey(Region,on_delete=models.CASCADE)
    building=models.ForeignKey(Building,on_delete=models.CASCADE)
    apartment=models.ManyToManyField(Apartment,related_name='special_services_apartments')
    auto_renew_enable=models.BooleanField(default=True)
    discounted_price=models.FloatField(blank=True,null=True)
    worker=models.ForeignKey(User,on_delete=models.CASCADE)
    created_at=models.DateField(auto_now_add=True,null=True,blank=True)
    # package=models.ManyToManyField(FeatureModel)
    updated_at=models.DateField(auto_now=True,null=True,blank=True)
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

auditlog.register(SpecialServicesModel)

CHOISE_RATING=(
('1','1'),
('2','2'),
('3','3'),
('4','4'),
('5','5')
)
class RatingModelForService(models.Model):
   client=models.ForeignKey(User,on_delete=models.CASCADE)
   service=models.ForeignKey(SpecialServicesModel,on_delete=models.CASCADE)
   Rating=models.CharField(max_length=200,choices=CHOISE_RATING)
   review_message=models.CharField(blank=True,null=True)
   created_at=models.DateTimeField(auto_now_add=True,null=True,blank=True)
   updated_at=models.DateField(auto_now=True,null=True,blank=True)

