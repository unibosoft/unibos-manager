"""
Production settings for UNIBOS
For deployment on Ubuntu/Oracle VM
"""

import os
from pathlib import Path

# Build paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# FIRST: Import base settings
from .base import *

# THEN: Override for production

# Database - Production PostgreSQL
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

# Static and Media files
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Security settings
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-production-key-change-this!')
DEBUG = False  # Set to True temporarily for debugging

# Hosts
ALLOWED_HOSTS = [
    'recaria.org',
    'www.recaria.org',
    '.recaria.org',
    '158.178.201.117',
    'rocksteady.local',
    'unibos.local',
    'localhost',
    '127.0.0.1',
    '*',  # Temporary for testing
]

# CSRF Settings - CRITICAL: These override base.py
CSRF_COOKIE_SECURE = False  # Set to True when HTTPS is properly configured
SESSION_COOKIE_SECURE = False  # Set to True when HTTPS is properly configured
CSRF_COOKIE_HTTPONLY = False  # Allow JavaScript access
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Lax'
SESSION_COOKIE_SAMESITE = 'Lax'

# CRITICAL: CSRF Trusted Origins - MUST include all possible origins
CSRF_TRUSTED_ORIGINS = [
    'https://recaria.org',
    'https://www.recaria.org',
    'http://recaria.org',
    'http://www.recaria.org',
    'https://158.178.201.117',
    'http://158.178.201.117',
    'http://158.178.201.117:8000',
    'https://158.178.201.117:8000',
    'http://localhost',
    'https://localhost',
    'http://localhost:8000',
    'https://localhost:8000',
    'http://127.0.0.1',
    'https://127.0.0.1',
    'http://127.0.0.1:8000',
    'https://127.0.0.1:8000',
    'http://rocksteady.local',
    'https://rocksteady.local',
]

# CORS Settings (if needed)
CORS_ALLOWED_ORIGINS = [
    'https://recaria.org',
    'https://www.recaria.org',
    'http://localhost:8000',
    'http://127.0.0.1:8000',
]
CORS_ALLOW_CREDENTIALS = True

# Email Configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'mail.recaria.org'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False
EMAIL_HOST_USER = 'berk@recaria.org'
EMAIL_HOST_PASSWORD = 'Recaria2025Mail!'
DEFAULT_FROM_EMAIL = 'berk@recaria.org'
SERVER_EMAIL = 'berk@recaria.org'

# Security Headers
SECURE_SSL_REDIRECT = False  # Set to True when HTTPS is properly configured
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_BROWSER_XSS_FILTER = True
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'