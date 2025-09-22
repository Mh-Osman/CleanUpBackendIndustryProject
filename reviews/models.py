from django.db import models

# Create your models here.
from django.conf import settings
from services_pakages.models import ServiceAssignment



class Rating(models.Model):
    assignment = models.OneToOneField(
        "ServiceAssignment",
        on_delete=models.CASCADE,
        related_name="rating"
    )
    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="given_ratings",
        limit_choices_to={'user_type': 'client'}
    )
    overall_rating = models.PositiveSmallIntegerField(default=5)   # 1–5 ⭐
    review = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.overall_rating}⭐ for {self.assignment}"
    
class EmployeeRating(models.Model):
    rating = models.ForeignKey(
        Rating, on_delete=models.CASCADE, related_name="employee_ratings"
    )
    employee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="ratings_received",
        limit_choices_to={'user_type': 'employee'}
    )
    score = models.PositiveSmallIntegerField(default=5)
    comment = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ("rating", "employee")

    def __str__(self):
        return f"{self.employee.username} got {self.score}⭐"