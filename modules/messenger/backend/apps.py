"""
Messenger Module Django App Configuration
"""

from django.apps import AppConfig


class MessengerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'modules.messenger.backend'
    label = 'messenger'
    verbose_name = 'Messenger'

    def ready(self):
        # Import signals when app is ready
        try:
            from . import signals  # noqa
        except ImportError:
            pass
