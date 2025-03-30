import os

from celery import Celery
from celery.schedules import crontab
from django.apps import apps 
import datetime
import pytz

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'snakefront.settings')

app = Celery('snakefront')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks(lambda: [n.name for n in apps.get_app_configs()])

@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))