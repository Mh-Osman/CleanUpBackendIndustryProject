from django.db import models
from users.models import CustomUser

# Create your models here.
class LeaseFormModel(models.Model):
    title = models.CharField(max_length=100)
    note = models.TextField()
    building = models.CharField(max_length=100)
    apartment = models.CharField(max_length=100)
    client = models.CharField(max_length=100)
    last_uploaded = models.DateTimeField(auto_now=True)
    client_signature = models.ImageField(upload_to='signatures/', null=True, blank=True)
    employee_signature = models.ImageField(upload_to='signatures/', null=True, blank=True)
    employee_name = models.CharField(max_length=100, null=True, blank=True)
    def __str__(self):
        return self.title

choices = [
    ('Excellent', 'Excellent'),
    ('Good', 'Good'),
    ('Average', 'Average'),
    ('Below Average', 'Below Average'),
    ('Poor', 'Poor'),
]
class SupervisorFormModel(models.Model):
   title = models.CharField(max_length=100)
   supervisor = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="supervisor_forms", limit_choices_to={'user_type': 'supervisor'})
   employee = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="employee_forms", limit_choices_to={'user_type': 'employee'})
   report_date = models.DateField(auto_now_add=True) #assign auto now_add=True for automatic date
   work_summary = models.TextField() # Summary of work 
   supervisor_comments = models.TextField(null=True, blank=True)
   issues_reported = models.TextField(null=True, blank=True)
   attachments = models.FileField(upload_to='supervisor_forms/', null=True, blank=True)
   report_summary = models.TextField(null=True, blank=True)
   performance =  models.CharField(max_length=20, choices=choices, null=True, blank=True) # Performance rating
   remark = models.TextField(null=True, blank=True) # Additional remarks
   last_updated = models.DateTimeField(auto_now=True)
   created_at = models.DateTimeField(auto_now_add=True)
   def __str__(self):
         return f"Supervisor Report by {self.supervisor.name} for {self.employee.name} on {self.report_date}"
   

   