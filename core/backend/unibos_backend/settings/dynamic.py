"""
Dynamic settings that work both locally and remotely
Auto-detects environment and configures accordingly
"""
import os
import socket
from pathlib import Path
from .base import *

# Auto-detect environment
HOSTNAME = socket.gethostname().lower()
IS_REMOTE = 'rocksteady' in HOSTNAME or 'ubuntu' in HOSTNAME or 'recaria' in HOSTNAME
IS_LOCAL = not IS_REMOTE

# Debug based on environment
DEBUG = IS_LOCAL

# Allowed hosts
ALLOWED_HOSTS = ['*']

# Database - PostgreSQL for both environments
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'unibos_db'),
        'USER': os.environ.get('DB_USER', 'unibos_user'),
        'PASSWORD': os.environ.get('DB_PASSWORD', 'unibos_password'),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}

if IS_REMOTE:
    print("🌍 Using PostgreSQL (remote)")
else:
    print("💻 Using PostgreSQL (local)")

# Security - HTTP compatible
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SECURE_SSL_REDIRECT = False

# Static files - create dir if needed
STATIC_URL = '/static/'
if IS_REMOTE:
    STATIC_ROOT = '/opt/unibos/static'
    os.makedirs(STATIC_ROOT, exist_ok=True)
else:
    STATIC_ROOT = BASE_DIR / 'staticfiles'

# CSRF
CSRF_TRUSTED_ORIGINS = [
    'http://localhost:8000',
    'http://127.0.0.1:8000',
    'http://rocksteady.local',
    'http://recaria.org',
    'https://recaria.org',
]

print(f"✅ Dynamic settings loaded - {'REMOTE' if IS_REMOTE else 'LOCAL'} environment")
