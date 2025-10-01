from django.apps import AppConfig


class clientProfilesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'clientProfiles'
    

    def ready(self):
        import clientProfiles.signals