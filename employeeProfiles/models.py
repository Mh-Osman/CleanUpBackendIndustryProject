from django.db import models
from users.models import CustomUser
from locations.models import Apartment
from django.utils.timezone import now
# Create your models here.
class EmployeeProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name="employee_profile")
    department = models.CharField(max_length=100, default="Cleaning")      # Eg: Cleaning, Maintenance
    shift = models.CharField(max_length=50, choices=[("morning","Morning"),("evening","Evening")])
    hire_date = models.DateField(auto_now_add=True)
    location = models.CharField(max_length=255, null=True, blank=True)     # City / Branch
    is_on_leave = models.BooleanField(default=False)
    avatar = models.ImageField(upload_to="employee_avatars/", null=True, blank=True)  # Profile Picture
    

    

    def __str__(self):
        return f"Employee: {self.user.username} ({self.department})"
    
class EmployeeSalary(models.Model):
    employee = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="salaries" , limit_choices_to={'role': 'employee'})
    month = models.DateField()                   # Which month
    base_salary = models.DecimalField(max_digits=10, decimal_places=2)
    performance_bonus = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    deductions = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    paid_on = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ("employee", "month")  # one salary per month
    def save(self, *args, **kwargs):
        # total_paid auto calculate হবে
        self.total_paid = self.base_salary + self.performance_bonus - self.deductions
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Salary: {self.employee.username} - {self.month.strftime('%B %Y')} ({self.total_paid})"

class EmployeeApartmentAssignment(models.Model):
    employee = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="assignments")
    apartment = models.ForeignKey("locations.Apartment", on_delete=models.CASCADE, related_name="assigned_employees")
    assigned_on = models.DateField(auto_now_add=True)
    role = models.CharField(max_length=100, default="Cleaner")  # Eg: Cleaner, Supervisor
    is_active = models.BooleanField(default=True)  # Current assignment status  
    end_date = models.DateField(null=True, blank=True)  # Assignment end date when is_active=False date will be set automatically

    class Meta:
        unique_together = ("employee", "apartment")  # এক employee একই apartment-এ একাধিকবার যাবে না
    
    def save(self, *args, **kwargs):
        if not self.is_active and self.end_date is None:
            self.end_date = now().date()
        super().save(*args, **kwargs)
    
    def __str__(self):
        status = "Active" if self.is_active else f"Ended on {self.end_date}"
        return f"Assignment: {self.employee.username} to {self.apartment.code} ({self.role}) - {status}"