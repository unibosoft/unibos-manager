"""
Sync module Django app configuration
"""

from django.apps import AppConfig


class SyncConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core.system.sync.backend'
    label = 'sync'
    verbose_name = 'Data Sync'
