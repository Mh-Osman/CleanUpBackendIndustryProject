from django.db import models

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
    