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


class SupervisorFormModel(models.Model):
   title = models.CharField(max_length=100)
   supervisor = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="supervisor_forms", limit_choices_to={'user_type': 'employee'})
   employee = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="employee_forms", limit_choices_to={'user_type': 'employee'})
   report_date = models.DateField()
   work_summary = models.TextField()
   supervisor_comments = models.TextField(null=True, blank=True)
   issues_reported = models.TextField(null=True, blank=True)
   attachments = models.FileField(upload_to='supervisor_forms/', null=True, blank=True)
   report_summary = models.TextField(null=True, blank=True)
   last_updated = models.DateTimeField(auto_now=True)
   created_at = models.DateTimeField(auto_now_add=True)
   def __str__(self):
         return f"Supervisor Report by {self.supervisor.name} for {self.employee.name} on {self.report_date}"
   

   