from django.db import models
from django.conf import settings
from locations.models import Apartment,Building,Region
from services_pakages.models import Category
from datetime import datetime,timezone
from clientProfiles.models import ClientProfile
from django.contrib.auth import get_user_model
from auditlog.registry import auditlog

User=get_user_model()
# Create your models here.
#salah uddin added a special services option

class SpecialService(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    building = models.ForeignKey('locations.Building', on_delete=models.CASCADE, related_name='special_services')
    apartment = models.ForeignKey('locations.Apartment', on_delete=models.CASCADE, related_name='special_services', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
 


class PlanModel(models.Model): 
    name = models.CharField(max_length=100)  
    plan_code = models.CharField(max_length=50, unique=True)  
    # stripe_price_id = models.CharField(max_length=100) 
    amount = models.FloatField()  
    interval = models.CharField(
        max_length=20,
        choices=(("month", "Monthly"), ("year", "Yearly"),("day", "Daily")),
        default="month"
    )
    description = models.TextField(blank=True, null=True)  
    is_active = models.BooleanField(default=True)
    category=models.ForeignKey(Category,on_delete=models.CASCADE,null=True,blank=True)
    #extra added
    # service=models.ManyToManyField('assign_task_employee.FeatureModel',blank=True) 
    discount=models.FloatField(blank=True,null=True,default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    auto_renewal=models.BooleanField(default=True,null=True,blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.plan_code} - {self.name}'
    # @property
    # def amount_after_discount(self):
    #     return self.amount-self.discount

class ServiceLineItem(models.Model):
    plan=models.ForeignKey(PlanModel,on_delete=models.CASCADE, related_name="service_line_items")
    name=models.CharField(max_length=100,blank=True,null=True)
    description = models.CharField(max_length=255,null=True,blank=True)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0,blank=True,null=True)

    def __str__(self):
        return f'{self.name}  {self.id}  {self.description}'


auditlog.register(PlanModel)
auditlog.register(ServiceLineItem)

class Subscription(models.Model):
    STATUS_CHOICES = (
        ("active","Active"),
        ("inactive","Inactive"),
        ("paused","Paused"),
        ("canceled","Canceled"),
        ("past_due","past_due"),
    )
    #salah uddin
    PAYMENT=(
        ('prepaid','prepaid'),
        ('postpaid','postpaid'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE,null=True,blank=True)
    plan = models.ForeignKey("PlanModel", on_delete=models.SET_NULL, null=True)
    building = models.ForeignKey(Building, on_delete=models.SET_NULL, null=True, blank=True)
    apartment = models.ForeignKey(Apartment, on_delete=models.SET_NULL, null=True, blank=True)
    region = models.ForeignKey(Region, on_delete=models.SET_NULL, null=True, blank=True)
    payment=models.CharField(choices=PAYMENT,blank=True,null=True,max_length=10,default='prepaid') #salah uddin
    # stripe_customer_id = models.CharField(max_length=100, blank=True, null=True)
    # stripe_subscription_id = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="active")
    start_date = models.DateField(null=True, blank=True)
   
    current_period_end = models.DateField(null=True, blank=True)
    pause_until = models.DateTimeField(null=True, blank=True)  # for paused subscriptions
    created_at = models.DateTimeField(auto_now_add=True,null=True,blank=True)
    updated_at = models.DateTimeField(auto_now=True,null=True,blank=True)
    employee=models.ManyToManyField(User,related_name='subscription_employee')



    def __str__(self):
        return f"{self.user} - {self.plan} ({self.status}) id is {self.id}"

auditlog.register(Subscription)






class SubscriptionHistory(models.Model):
    subscription = models.ForeignKey(Subscription, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=50)  
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True) 
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'{self.action} {self.amount} {self.created_at}'


invoice_status=(
    ('paid','paid'),
    ('unpaid','unpaid')
)

class InvoiceModel(models.Model):
    INVOICE_TYPE_CHOICES = [
        ("outgoing", "Outgoing (Sales)"),
        ("incoming", "Incoming (Expenses)"),
    ]
    
    invoice_id = models.CharField(max_length=100, unique=True)
    type = models.CharField(max_length=20, choices=INVOICE_TYPE_CHOICES)
    date_issued = models.DateField()
    due_date = models.DateField(null=True, blank=True)
    status=models.CharField(choices=invoice_status,blank=True,null=True)
    building = models.ForeignKey(Building, on_delete=models.SET_NULL,null=True,blank=True)
    client = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    apartments = models.ManyToManyField(Apartment)
    plan = models.ForeignKey(PlanModel, on_delete=models.SET_NULL, null=True, blank=True)
    vendor_name=models.CharField(blank=True,null=True)
    vendor= models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,related_name='invoice_vendor')
    vendor_invoice_file = models.FileField(upload_to="vendor_invoices", blank=True, null=True)
    note = models.TextField(blank=True, null=True)
    file = models.FileField(upload_to="invoices", blank=True, null=True)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    expense_category=models.ManyToManyField(Category)
    @property
    def calculated_total(self):
        return sum(item.total for item in self.line_items.all())

    def __str__(self):
        return f"{self.invoice_id} - {self.type}"


class InvoiceLineItem(models.Model):
    invoice = models.ForeignKey(InvoiceModel, on_delete=models.CASCADE, related_name="line_items")
    description = models.CharField(max_length=255,null=True,blank=True)
    service = models.ForeignKey('assign_task_employee.FeatureModel', on_delete=models.CASCADE, null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0,blank=True,null=True)
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0,null=True,blank=True)

    @property
    def total(self):
        return (self.quantity * self.unit_price) - self.discount + self.tax

