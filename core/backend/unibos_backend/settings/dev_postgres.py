"""
Development settings with PostgreSQL - Based on emergency settings
"""

from .emergency import *

# Override database to use PostgreSQL
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'unibos_db',
        'USER': 'unibos_user',
        'PASSWORD': 'unibos_pass',
        'HOST': 'localhost',
        'PORT': '5432',
        'OPTIONS': {
            'connect_timeout': 10,
        }
    }
}

# Connection pooling
DATABASES['default']['CONN_MAX_AGE'] = 60

# Use Django's default cache instead of Redis for development
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}

# Debug toolbar for development
if DEBUG:
    # Convert MIDDLEWARE to list if it's a tuple
    MIDDLEWARE = list(MIDDLEWARE)
    
    # Add debug_toolbar to INSTALLED_APPS
    INSTALLED_APPS = list(INSTALLED_APPS)
    INSTALLED_APPS.append('debug_toolbar')
    
    # Add debug_toolbar middleware
    MIDDLEWARE.insert(0, 'debug_toolbar.middleware.DebugToolbarMiddleware')
    
    # Internal IPs for debug toolbar
    INTERNAL_IPS = ['127.0.0.1', 'localhost']
    
    # Debug toolbar settings
    DEBUG_TOOLBAR_CONFIG = {
        'SHOW_TOOLBAR_CALLBACK': lambda request: DEBUG,
    }

print("📘 Using PostgreSQL database configuration")