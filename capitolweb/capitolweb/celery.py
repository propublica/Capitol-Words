from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery import shared_task

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'capitolweb.settings')
app = Celery('capitolweb')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
