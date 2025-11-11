"""
Simple development settings for quick startup
"""
from .base import *

# Remove problematic apps temporarily
INSTALLED_APPS = [app for app in INSTALLED_APPS if app not in [
    'channels',
    'django_prometheus', 
    'debug_toolbar',
    'django_seed',
    'health_check',
    'health_check.db',
    'health_check.cache',
    'health_check.storage',
    'health_check.contrib.celery',
    'health_check.contrib.redis',
]]

# Remove prometheus middleware
MIDDLEWARE = [m for m in MIDDLEWARE if 'prometheus' not in m]

# PostgreSQL database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'unibos_db',
        'USER': 'unibos_user',
        'PASSWORD': 'unibos_password',
        'HOST': 'localhost',
        'PORT': '5432',
        'CONN_MAX_AGE': 60,
        'OPTIONS': {
            'connect_timeout': 10,
        }
    }
}

# Disable celery for now
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

# Allow all hosts for development
ALLOWED_HOSTS = ['*']

# CORS settings
CORS_ALLOW_ALL_ORIGINS = True

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media files - Universal Data Directory
MEDIA_URL = '/media/'
DATA_DIR = BASE_DIR.parent.parent.parent / 'data'
MEDIA_ROOT = DATA_DIR / 'runtime' / 'media'

# Simplified logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}

# Disable ASGI
WSGI_APPLICATION = 'unibos_backend.wsgi.application'