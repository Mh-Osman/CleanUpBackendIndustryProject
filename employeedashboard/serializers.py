from rest_framework import serializers
from .models import LeaseFormModel

class LeaseFormSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaseFormModel
        fields = '__all__'
from .models import SupervisorFormModel
class SupervisorFormSerializer(serializers.ModelSerializer):
    supervisor_name = serializers.CharField(source='supervisor.name', read_only=True)
    employee_name = serializers.CharField(source='employee.name', read_only=True)
    employee_email = serializers.EmailField(source='employee.email', read_only=True)  # Adding employee email field

    class Meta:
        model = SupervisorFormModel
        fields = [
            'id',
            'title',
            'supervisor',              # Still including the foreign key for validation or reference
            'employee',                # Same as above
            'supervisor_name',         # Adding custom field for supervisor's name
            'employee_name',           # Adding custom field for employee's name
            'employee_email',          # Adding custom field for employee's email
            'report_date',
            'work_summary',
            'supervisor_comments',
            'issues_reported',
            'attachments',
            'report_summary',
            'performance',
            'remark',
            'last_updated',
            'created_at',
        ]
