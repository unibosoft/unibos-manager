"""
Production settings for UNIBOS - HTTP mode
For deployment without SSL certificates
"""

from .base import *
import os

DEBUG = False
ALLOWED_HOSTS = ['*']

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'unibos_central'),
        'USER': os.environ.get('DB_USER', 'unibos_admin'),
        'PASSWORD': os.environ.get('DB_PASSWORD', 'unibos_password'),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}

# Security - Modified for HTTP
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-production-key-change-this!')
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False  # Allow HTTP
CSRF_COOKIE_SECURE = False     # Allow HTTP
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True

# Session settings
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_AGE = 86400  # 24 hours
SESSION_COOKIE_SAMESITE = 'Lax'

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = '/opt/unibos/static'
MEDIA_URL = '/media/'
MEDIA_ROOT = '/opt/unibos/media'

# CSRF trusted origins
CSRF_TRUSTED_ORIGINS = [
    'http://rocksteady.local',
    'http://localhost:8000',
    'http://158.178.201.117:8000',
]

# Password hashers (ensure compatibility)
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    'django.contrib.auth.hashers.Argon2PasswordHasher',
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
]
