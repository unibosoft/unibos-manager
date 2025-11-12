"""
Core Domain Models (Essentials)
Shared models used across all modules
"""

# Django app configuration
default_app_config = 'core.models.apps.CoreModelsConfig'

__all__ = [
    'BaseModel',
    'ItemCategory',
    'Unit',
    'Item',
    'ItemPrice',
    'Account',
    'UserProfile',
]

# Lazy imports to avoid AppRegistryNotReady error
def __getattr__(name):
    if name in __all__:
        from .base import BaseModel, ItemCategory, Unit, Item, ItemPrice, Account, UserProfile
        return locals()[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
