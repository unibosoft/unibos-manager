"""
Core Models Django App Configuration
"""
from django.apps import AppConfig


class CoreModelsConfig(AppConfig):
    """Configuration for core shared models"""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core.models'
    label = 'core_models'
    verbose_name = 'Core Models'
