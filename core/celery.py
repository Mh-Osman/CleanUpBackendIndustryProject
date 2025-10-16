# myproject/celery.py
import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

app = Celery("core")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

from celery.schedules import crontab

app.conf.beat_schedule = {
    "auto-cancel-subscriptions-daily": {
        "task": "plan.tasks.auto_cancel_expired_subscriptions",
        "schedule": crontab(hour=3, minute=2),  # every day at midnight
    },
}

from celery.schedules import crontab

app.conf.beat_schedule = {
    "auto-cancel-subscriptions-daily": {
        "task": "plan.tasks.auto_cancel_expired_subscriptions",
        "schedule": crontab(),  # runs every minute
    },
}
