from django.apps import AppConfig


class DynamicformConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'dynamicForm'

    def ready(self):
        import dynamicForm.signals
