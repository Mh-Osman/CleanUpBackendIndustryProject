from django.apps import AppConfig


class AssignTaskEmployeeConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'assign_task_employee'
    def ready(self):
        import assign_task_employee.signals