from django.contrib import admin

# Register your models here.
from  dynamicForm.models import FormNameModel, FormFieldModel, FormSubmissionModel
admin.site.register(FormNameModel)
admin.site.register(FormFieldModel)
admin.site.register(FormSubmissionModel)