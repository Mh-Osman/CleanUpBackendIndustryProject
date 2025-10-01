from django.db import models
from services_pakages.models import Category
from django.contrib.auth import get_user_model
User=get_user_model()
# Create your models here.

CHOICE_STATUS=(
    ('Submitted','submitted'),
    ('Approved','Approved'),
    ('Cancel','Cancel'),
)

class InvoiceRequestFromEmployee(models.Model):
    vendor_name=models.CharField(max_length=100)
    vendor=models.ForeignKey(User,on_delete=models.CASCADE)
    expense_category=models.ManyToManyField(Category)
    expense_date=models.DateField()
    discription=models.TextField()
    receipt=models.ImageField(blank=True,null=True)
    amount=models.IntegerField()
    status=models.CharField(choices=CHOICE_STATUS,default='Submitted')


