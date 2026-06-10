import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mumaid.settings.dev")

app = Celery("momaid")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
