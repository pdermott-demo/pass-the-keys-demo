import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pass_the_keys_demo.settings")

celery_app = Celery("pass_the_keys_demo")
celery_app.config_from_object("django.conf:settings", namespace="CELERY")
celery_app.autodiscover_tasks()
