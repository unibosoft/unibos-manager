"""
UNIBOS SDK - Module Development Kit

This package provides tools and utilities for developing UNIBOS modules.
All modules should use this SDK to integrate with the UNIBOS platform.

Usage:
    from unibos_sdk import UnibosModule

    class MyModule(UnibosModule):
        def __init__(self):
            super().__init__('my_module')

Version: 1.0.0
"""

__version__ = '1.0.0'
__author__ = 'Berk Hatırlı'

from .base import UnibosSdkBase
from .module import UnibosModule
from .auth import UnibosAuth
from .storage import UnibosStorage
from .cache import UnibosCache
from .events import UnibosEvents

__all__ = [
    'UnibosSdkBase',
    'UnibosModule',
    'UnibosAuth',
    'UnibosStorage',
    'UnibosCache',
    'UnibosEvents',
]
