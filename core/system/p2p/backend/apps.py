from django.apps import AppConfig


class P2PConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core.system.p2p.backend'
    label = 'p2p'
    verbose_name = 'P2P Communication'

    def ready(self):
        # Import signals if needed
        pass
