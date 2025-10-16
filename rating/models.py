from django.db import models
from django.conf import settings
# Create your models here.
from django.contrib.auth import get_user_model
User = get_user_model()
CHOICES_RATING = (
    ('1', '1'),
    ('2', '2'),
    ('3', '3'), 
    ('4', '4'),
    ('5', '5')

)

class RatingModel(models.Model):
    employee = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_rating")
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name="client_rating" , limit_choices_to={'user_type': 'client'} , null=True, blank=True)
    rating = models.CharField(max_length=1, choices=CHOICES_RATING)
    review = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Rating by {self.client.name} - {self.rating} to {self.employee.name}'