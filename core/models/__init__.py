"""
Core Domain Models (Essentials)
Shared models used across all modules
"""
from .base import BaseModel, ItemCategory, Unit, Item, ItemPrice, Account, UserProfile

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
