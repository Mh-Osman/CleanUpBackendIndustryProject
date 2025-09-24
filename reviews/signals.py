from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Rating, EmployeeRating

@receiver(post_save, sender=Rating)
def create_employee_ratings(sender, instance, created, **kwargs):
    if created:
        employees = instance.assignment.employees.all()
        for emp in employees:
            EmployeeRating.objects.create(
                rating=instance,
                employee=emp,
                score=instance.overall_rating
            )