
from django.urls import include, path

from dynamicForm.views import CreateDynamicFormView, FormNameViewSet, FormSubmissionViewSet, SubmitDynamicFormView, getallformswithsubmissionsanswers, getformWithSubmissionsAnswers 
from rest_framework.routers import DefaultRouter
router = DefaultRouter()
# >>>>>>> gani

router.register(r'forms', FormNameViewSet, basename='form-name')
router.register(r'form-submissions', FormSubmissionViewSet, basename='form-submission')

urlpatterns = [
    path('', include(router.urls)),
    path('create-form/', CreateDynamicFormView, name='create_dynamic_form'),
    path('submit-form/<int:form_id>/', SubmitDynamicFormView, name='submit_dynamic_form'),
    path('getformWithSubmissionsAnswers/<int:form_id>/', getformWithSubmissionsAnswers, name='get_form_submissions'),
    path('getallformswithsubmissionsanswers/', getallformswithsubmissionsanswers, name='get_all_forms_submissions'),
]