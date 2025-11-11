"""
Production settings for UNIBOS
For deployment on Ubuntu/Oracle VM
"""

import os
from pathlib import Path

# Import base settings
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Database - Centralized PostgreSQL
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'unibos_db'),
        'USER': os.environ.get('DB_USER', 'unibos_user'),
        'PASSWORD': os.environ.get('DB_PASSWORD', 'unibos_password'),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
        'OPTIONS': {
            'connect_timeout': 10,
        },
        'CONN_MAX_AGE': 600,
        'ATOMIC_REQUESTS': True,
    }
}

# Static files - production uses same structure as development for consistency
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Import base settings - MEDIA_ROOT and DATA_DIR will be inherited from base.py
# Universal Data Directory Structure:
#   Local: /Users/berkhatirli/Desktop/unibos/data/
#   Production: /var/www/unibos/data/
# This ensures local/production parity for all data file handling
from .base import *

# Security - AFTER base import to override
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-production-key-change-this!')
SECURE_SSL_REDIRECT = False
# HTTPS is enabled, so enable secure cookies
SESSION_COOKIE_SECURE = True  # Enable for HTTPS
CSRF_COOKIE_SECURE = True     # Enable for HTTPS
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = False   # Changed to False to allow JavaScript access
SESSION_COOKIE_SAMESITE = 'Lax'
X_FRAME_OPTIONS = 'DENY'

# CSRF trusted origins for HTTPS - AFTER base import to ensure it's not overridden
CSRF_TRUSTED_ORIGINS = [
    'https://recaria.org',
    'https://www.recaria.org',
    'http://recaria.org',
    'http://www.recaria.org',
    'https://158.178.201.117',
    'http://158.178.201.117:8000',
    'http://localhost:8000',
    'https://localhost:8000',
]

# Email Configuration for recaria.org - AFTER base import
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'mail.recaria.org'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False
EMAIL_HOST_USER = 'berk@recaria.org'
EMAIL_HOST_PASSWORD = 'Recaria2025Mail!'
DEFAULT_FROM_EMAIL = 'berk@recaria.org'
SERVER_EMAIL = 'berk@recaria.org'

# Then override for production
DEBUG = False

# Override ALLOWED_HOSTS from base
ALLOWED_HOSTS = [
    'rocksteady.local',
    'unibos.local', 
    'localhost',
    '127.0.0.1',
    '158.178.201.117',
    'recaria.org',
    'www.recaria.org',
    '.recaria.org',
    '*'  # For testing, restrict in real production
]