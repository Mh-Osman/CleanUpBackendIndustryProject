from rest_framework.decorators import api_view, permission_classes
from rest_framework import permissions
from rest_framework.response import Response
from dynamicForm.models import FormNameModel, FormFieldModel
from dynamicForm.models import FormSubmissionModel
from rest_framework import viewsets

@api_view(['POST'])
@permission_classes([permissions.IsAdminUser])
def CreateDynamicFormView(request):
    user = request.user

    # ✅ Get data from JSON body
    form_name = request.data.get('form_name')
    form_fields = request.data.get('form_level', [])
    form_types = request.data.get('form_types', [])
    form_required = request.data.get('form_required', [])
    form_options = request.data.get('form_options', [])

    # ✅ Check required field
    if not form_name:
        return Response({'error': 'form_name is required'}, status=400)

    # ✅ Create form instance
    form_instance = FormNameModel.objects.create(form_name=form_name, admin=user)

    # ✅ Create dynamic fields
    for field, field_type, required, options in zip(form_fields, form_types, form_required, form_options):
        FormFieldModel.objects.create(
            form=form_instance,
            field_label=field,
            field_type=field_type,
            is_required=str(required).lower() == 'true',
            options=options
        )

    return Response({'status': 'Form created successfully'})



from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import permissions, status
from dynamicForm.models import FormNameModel, FormSubmissionModel
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt  # Disable CSRF for API calls (Postman)
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])  # or IsAdminUser
def SubmitDynamicFormView(request, form_id):
    try:
        form_instance = FormNameModel.objects.get(id=form_id)
    except FormNameModel.DoesNotExist:
        return Response({'error': 'Form not found'}, status=status.HTTP_404_NOT_FOUND)

    submission_data = {}

    for field in form_instance.fields.all():
        field_value = request.data.get(field.field_label)
        if field_value is None and field.is_required:
            return Response(
                {'error': f'Missing required field: {field.field_label}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        submission_data[field.field_label] = field_value

    FormSubmissionModel.objects.create(
        form=form_instance,
        data=submission_data,
        response_user=request.user
    )

    return Response({
        'status': 'Form submitted successfully',
        'submitted_data': submission_data
    }, status=status.HTTP_201_CREATED)

@csrf_exempt    
@api_view(['GET'])
@permission_classes([permissions.IsAdminUser])
def getformWithSubmissionsAnswers(request, form_id):
    try:
        form_instance = FormNameModel.objects.get(id=form_id)
    except FormNameModel.DoesNotExist:
        return Response({'error': 'Form not found'}, status=status.HTTP_404_NOT_FOUND)

    submissions = form_instance.submissions.all()
    submissions_data = [
        {
            'submitted_at': submission.submitted_at,
            'data': submission.data
        }
        for submission in submissions
    ]

    return Response({
        'form_name': form_instance.form_name,
        'submissions': submissions_data
    }, status=status.HTTP_200_OK)  


from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import FormNameModel

@api_view(['GET'])
def getallformswithsubmissionsanswers(request):
    forms = FormNameModel.objects.all()
    all_forms_data = []

    for form in forms:
        submissions = form.submissions.all()
        submissions_data = [
            {
                'submitted_at': submission.submitted_at,
                'data': submission.data
            }
            for submission in submissions
        ]
        form_data = {
            'id': form.id,  # <-- form id add here
            'form_name': form.form_name,
            'submissions': submissions_data
        }
        all_forms_data.append(form_data)

    return Response({
        'forms': all_forms_data
    }, status=status.HTTP_200_OK)



from rest_framework import permissions
from dynamicForm.serializers import FormNameSerializer, FormSubmissionSerializer
from rest_framework import generics, filters

class FormNameViewSet(viewsets.ModelViewSet):
    queryset = FormNameModel.objects.all()
    # permission_classes = [permissions.IsAdminUser]
    serializer_class = FormNameSerializer
    ordering_fields = ['-created_at']
    ordering = ['-created_at']  # default ordering
    search_fields = ['form_name']
   # filter_backends = [permissions.DjangoFilterBackend, permissions.SearchFilter]
   # filterset_fields = ['admin', 'created_at', "form_name"]
    #filterset_fields = ['admin']
    def get_permissions(self):
        if self.request.method in ["GET"]:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAdminUser()]

class FormSubmissionViewSet(viewsets.ModelViewSet):
    queryset = FormSubmissionModel.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = FormSubmissionSerializer
    search_fields = ['form__form_name', 'response_user__name', 'submitted_at']
    filterset_fields = ['form', 'response_user', 'submitted_at']
    ordering_fields = ['-submitted_at']
    ordering = ['-submitted_at']  # default ordering



