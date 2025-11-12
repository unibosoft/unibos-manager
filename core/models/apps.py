"""
Core Models Django App Configuration
"""
from django.apps import AppConfig


class CoreModelsConfig(AppConfig):
    """Configuration for core shared models"""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core.models'
    label = 'modules_core'  # Must match app_label in base.py models
    verbose_name = 'Core Models'
