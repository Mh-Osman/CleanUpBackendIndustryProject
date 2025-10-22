from rest_framework import serializers
from .models import LeaseFormModel

class LeaseFormSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaseFormModel
        fields = '__all__'

from rest_framework import serializers
from .models import SupervisorFormModel

class SupervisorFormSerializer(serializers.ModelSerializer):
    supervisor_name = serializers.CharField(source='supervisor.name', read_only=True)
    supervisor_mail = serializers.EmailField(source='supervisor.email', read_only=True)
    employee_name = serializers.CharField(source='employee.name', read_only=True)
    employee_mail = serializers.EmailField(source='employee.email', read_only=True)

    class Meta:
        model = SupervisorFormModel
        fields = [
            'id',
            'supervisor',
            'supervisor_name',
            'supervisor_mail',
            'employee',
            'employee_name',
            'employee_mail',
            'report_date',
            'work_summary',
            'performance',
            'supervisor_comments',
            'issues_reported',
            'created_at',
            'last_updated',
        ]
        read_only_fields = ['id', 'created_at', 'last_updated']
