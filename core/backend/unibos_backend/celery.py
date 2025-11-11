"""
Celery configuration for UNIBOS Backend
"""

import os
from celery import Celery
from celery.signals import setup_logging

# Set the default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'unibos_backend.settings.production')

# Create Celery app
app = Celery('unibos_backend')

# Load configuration from Django settings
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks from all registered Django apps
app.autodiscover_tasks()


@setup_logging.connect
def config_loggers(*args, **kwargs):
    """Configure Celery logging to use Django's logging configuration"""
    from logging.config import dictConfig
    from django.conf import settings
    dictConfig(settings.LOGGING)


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    """Debug task for testing Celery"""
    print(f'Request: {self.request!r}')