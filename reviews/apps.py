from django.apps import AppConfig
from django.db.models.signals import post_save
from django.dispatch import receiver

class ReviewsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'reviews'

    def ready(self):
        import reviews.signals  # 
