import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mumaid.settings")

app = Celery("mumaid")

app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks()

app.conf.broker_url = os.getenv("REDIS_URL")
app.conf.result_backend = os.getenv("REDIS_URL")