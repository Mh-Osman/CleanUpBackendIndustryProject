from django.db import models
from django.contrib.auth import get_user_model
user = get_user_model()
# Create your models here.
class FormNameModel(models.Model):
    form_name = models.CharField(max_length=200)
    admin = models.ForeignKey(user, on_delete=models.CASCADE, limit_choices_to={'is_staff': True})

    def __str__(self):
        return f"{self.form_name} created by {self.admin.username}"
    

class FormFieldModel(models.Model):
    FIELD_TYPES = [
        ('text', 'Text'),
        ('number', 'Number'),
        ('date', 'Date'),
        ('email', 'Email'),
        ('checkbox', 'Checkbox'),
        ('radio', 'Radio'),
        ('select', 'Select'),
    ]
    form = models.ForeignKey(FormNameModel, related_name='fields', on_delete=models.CASCADE)
    field_label = models.CharField(max_length=200)
    field_type = models.CharField(max_length=20, choices=FIELD_TYPES)
    is_required = models.BooleanField(default=False)
    options = models.TextField(blank=True, help_text="Comma-separated options for select, radio fields")

    def __str__(self):
        return f"{self.field_label} ({self.field_type}) in {self.form.form_name}"
    

class FormSubmissionModel(models.Model):
    form = models.ForeignKey(FormNameModel, related_name='submissions', on_delete=models.CASCADE)
    submitted_at = models.DateTimeField(auto_now_add=True)
    response_user = models.ForeignKey(user, on_delete=models.CASCADE, null=True, blank=True)
    data = models.JSONField()

    def __str__(self):
        return f"Submission for {self.form.form_name} at {self.submitted_at}"
