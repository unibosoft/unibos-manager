"""
Module Registry App Configuration
"""

from django.apps import AppConfig


class ModuleRegistryConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core.backend.core_apps.module_registry'
    verbose_name = 'UNIBOS Module Registry'

    def ready(self):
        """
        Called when Django starts.
        Initialize module registry and discover modules.
        """
        # Import signals if needed
        pass
