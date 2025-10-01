# clientProfiles/signals.py

from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from django.utils.timezone import now
from clientProfiles.models import ClientProfile
from users.models import CustomUser


@receiver(user_logged_in)
def update_last_login(sender, request, user, **kwargs):
    try:
        profile = user.client_profile
        profile.last_login = now()
        profile.save()
    except ClientProfile.DoesNotExist:
        pass  # যদি profile না থাকে, ignore করো