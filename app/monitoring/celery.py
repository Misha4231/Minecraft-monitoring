import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'monitoring.settings')
app = Celery('monitoring')

app.config_from_object('django.conf:settings', namespace='CELERY')


app.conf.beat_schedule = {
    'get_servers_info': {
        'task': 'serversApp.tasks.get_new_server_info',
        'schedule': 600
    },
    'get_new_donates': {
        'task': 'serversApp.tasks.get_new_donates',
        'schedule': 300,
    },
}

app.autodiscover_tasks()
