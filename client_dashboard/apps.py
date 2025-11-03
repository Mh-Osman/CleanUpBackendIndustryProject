from django.apps import AppConfig


class ClientDashboardConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'client_dashboard'
    def ready(self):
        import client_dashboard.signals
