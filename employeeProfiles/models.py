from django.db import models
from users.models import CustomUser
from locations.models import Apartment
from django.utils.timezone import now
# Create your models here.
class EmployeeProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name="employee_profile", limit_choices_to={'user_type': 'employee'})
    department = models.CharField(max_length=100, default="Cleaning")      # Eg: Cleaning, Maintenance
    role = models.CharField(max_length=100, default="Cleaner")            # Eg: Cleaner, Supervisor
    national_id = models.CharField(max_length=50, unique=True, null=True, blank=True)
    id_expiry = models.DateField(null=True, blank=True) #saudi arabia specific 
    contact_number = models.CharField(max_length=15, null=True, blank=True)
    shift = models.CharField(max_length=50, choices=[("morning","Morning"),("evening","Evening")])
    status = models.CharField(max_length=20, choices=[('Active','Active'), ('On Leave','On Leave')], default='Active',blank=True,null=True)
    contract_start = models.DateField(auto_now_add=True)
    contract_end = models.DateField(null=True, blank=True) #mannualy set
    location = models.CharField(max_length=255, null=True, blank=True)     # City / Branch
    is_on_leave = models.BooleanField(default=False)
    avatar = models.ImageField(upload_to="employee_avatars/", null=True, blank=True)  # Profile Picture
    salary_day = models.IntegerField(null=True, blank=True)  # মাসের কোন দিন salary দিবে
    base_salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # Default salary
    created_at = models.DateTimeField(auto_now_add=True)  # create time auto set
    updated_at = models.DateTimeField(auto_now=True)
    

    

    def __str__(self):
        return f"Employee: {self.user.name} ({self.department})"
    

    
class EmployeeSalary(models.Model):
    employee = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="salaries" , limit_choices_to={'user_type': 'employee'})
    month = models.DateField()                   # Which month
    performance_bonus = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    deductions = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    paid_on = models.DateTimeField(null=True, blank=True) # When salary was paid  date will be set automatically
    paid = models.BooleanField(default=False)  # Salary payment status

    class Meta:
        unique_together = ("employee", "month")  # one salary per month
    def save(self, *args, **kwargs):
        base_salary = 0
        if hasattr(self.employee, 'employee_profile') and self.employee.employee_profile.base_salary:
            base_salary = self.employee.employee_profile.base_salary
        self.total_paid = base_salary + self.performance_bonus - self.deductions
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Salary: {self.employee.name} - {self.month.strftime('%B %Y')} ({self.total_paid})"
    
    
from django.utils import timezone
class Attendance(models.Model):
    employee = models.ForeignKey(CustomUser, on_delete=models.CASCADE , related_name="attendances", limit_choices_to={'user_type': 'employee'})
    date = models.DateField(default=timezone.now)
    check_in = models.TimeField()
    expected_time = models.TimeField(default="09:00")
    on_time = models.BooleanField(null=True, blank=True)

    def save(self, *args, **kwargs):
        # শুধু প্রথমবার set হবে
        if self._state.adding and self.on_time is None:
            self.on_time = self.check_in <= self.expected_time
        super().save(*args, **kwargs)

class EmployeeApartmentAssignment(models.Model):
    employee = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="assignments")
    apartment = models.ForeignKey("locations.Apartment", on_delete=models.CASCADE, related_name="assigned_employees")
    assigned_on = models.DateField(auto_now_add=True)
    user_type = models.CharField(max_length=100, default="Cleaner")  # Eg: Cleaner, Supervisor
    is_active = models.BooleanField(default=True)  # Current assignment status  
    end_date = models.DateField(null=True, blank=True)  # Assignment end date when is_active=False date will be set automatically

    class Meta:
        unique_together = ("employee", "apartment")  # এক employee একই apartment-এ একাধিকবার যাবে না
    
    def save(self, *args, **kwargs):
        if not self.is_active and self.end_date is None: # assignment শেষ হলে end_date set হবে
            self.end_date = now().date()
        super().save(*args, **kwargs)
    
    def __str__(self):
        status = "Active" if self.is_active else f"Ended on {self.end_date}"
        return f"Assignment: {self.employee.name} to {self.apartment.code} ({self.user_type}) - {status}"