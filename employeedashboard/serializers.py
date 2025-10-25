from rest_framework import serializers
from .models import LeaseFormModel

class LeaseFormSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaseFormModel
        fields = '__all__'
# <<<<<<< HEAD

from rest_framework import serializers
from .models import SupervisorFormModel

class SupervisorFormSerializer(serializers.ModelSerializer):
    supervisor_name = serializers.CharField(source='supervisor.name', read_only=True)
    supervisor_mail = serializers.EmailField(source='supervisor.email', read_only=True)
    employee_name = serializers.CharField(source='employee.name', read_only=True)
    employee_mail = serializers.EmailField(source='employee.email', read_only=True)
# # =======
# from .models import SupervisorFormModel
# class SupervisorFormSerializer(serializers.ModelSerializer):
#     supervisor_name = serializers.CharField(source='supervisor.name', read_only=True)
#     employee_name = serializers.CharField(source='employee.name', read_only=True)
#     employee_email = serializers.EmailField(source='employee.email', read_only=True)  # Adding employee email field
# # >>>>>>> origin/testingallmerge

    class Meta:
        model = SupervisorFormModel
        fields = [
            'id',
# <<<<<<< HEAD
            'supervisor',
            'supervisor_name',
            'supervisor_mail',
            'employee',
            'employee_name',
            'employee_mail',
            'report_date',
            'work_summary',
            'report_summary',
            'performance',
            'supervisor_comments',
            'issues_reported',
            'created_at',
            'last_updated',
        ]
        read_only_fields = ['id', 'created_at', 'last_updated']
# # =======
#             'title',
#             'supervisor',              # Still including the foreign key for validation or reference
#             'employee',                # Same as above
#             'supervisor_name',         # Adding custom field for supervisor's name
#             'employee_name',           # Adding custom field for employee's name
#             'employee_email',          # Adding custom field for employee's email
#             'report_date',
#             'work_summary',
#             'supervisor_comments',
#             'issues_reported',
#             'attachments',
#             'report_summary',
#             'performance',
#             'remark',
#             'last_updated',
#             'created_at',
#         ]
# # >>>>>>> origin/testingallmerge
