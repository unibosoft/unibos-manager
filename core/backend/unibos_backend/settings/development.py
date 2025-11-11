"""
Development settings - PostgreSQL
"""
from .base import *

DEBUG = True
ALLOWED_HOSTS = ['*']

# PostgreSQL for local development
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'unibos_db',
        'USER': 'unibos_user',
        'PASSWORD': 'unibos_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# Security
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# CORS settings for Flutter web app
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

# Disable throttling in development for easier testing
REST_FRAMEWORK = {
    **REST_FRAMEWORK,
    'DEFAULT_THROTTLE_RATES': {
        'anon': '10000/hour',
        'user': '100000/hour',
        'burst': '6000/minute',
    },
}

print("💻 Development settings with PostgreSQL")
