"""
UNIBOS Hub Settings
Hub server deployment (rocksteady + bebop HA pair)

This settings file is optimized for the UNIBOS hub server:
- Identity Provider and user registry
- Node registry and coordination
- Central PostgreSQL database (unibos_db)
- Redis for caching and Celery
- Data sync coordination
- Service monitoring and health checks
"""

import os
from pathlib import Path

# Import base settings
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Import all base settings
from .base import *

# Override for hub production deployment
DEBUG = False

# Hub-specific allowed hosts
ALLOWED_HOSTS = [
    'rocksteady.local',
    'bebop.local',  # HA pair
    'unibos.local',
    'localhost',
    '127.0.0.1',
    '158.178.201.117',
    'recaria.org',
    'www.recaria.org',
    '.recaria.org',
    os.environ.get('HUB_HOST', 'localhost'),
]

# Database - Central PostgreSQL (production)
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
        'CONN_MAX_AGE': 600,  # Connection pooling for performance
        'ATOMIC_REQUESTS': True,
    }
}

# Redis - Central cache and Celery broker
REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': REDIS_URL,
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'SOCKET_CONNECT_TIMEOUT': 5,
            'SOCKET_TIMEOUT': 5,
            'COMPRESSOR': 'django_redis.compressors.zlib.ZlibCompressor',
            'CONNECTION_POOL_KWARGS': {
                'max_connections': 50,
                'retry_on_timeout': True,
            }
        },
        'KEY_PREFIX': 'unibos_hub',
        'TIMEOUT': 300,
    }
}

# Celery - Central task queue
CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = REDIS_URL
CELERY_TASK_ALWAYS_EAGER = False  # Run tasks asynchronously in production
CELERY_TASK_EAGER_PROPAGATES = False
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Europe/Istanbul'
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60  # 30 minutes max
CELERY_TASK_SOFT_TIME_LIMIT = 25 * 60  # 25 minutes soft limit
CELERY_WORKER_PREFETCH_MULTIPLIER = 1  # Fair task distribution
CELERY_RESULT_EXPIRES = 3600  # Results expire after 1 hour
CELERY_TASK_ACKS_LATE = True  # Tasks acknowledged after completion
CELERY_WORKER_HIJACK_ROOT_LOGGER = False  # Don't override logging

# Security - Production hardened
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-server-key-change-this!')
SECURE_SSL_REDIRECT = False  # Nginx handles SSL termination
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = False
SESSION_COOKIE_SAMESITE = 'Lax'
X_FRAME_OPTIONS = 'DENY'

# CSRF trusted origins
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

# Static files - Production
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Media files - Central storage
# Inherits DATA_DIR from base.py (UNIBOS_ROOT / 'data')
# Override via MEDIA_ROOT env var if needed
MEDIA_URL = '/media/'
MEDIA_ROOT = os.environ.get('MEDIA_ROOT', str(DATA_DIR / 'media'))

# Email - Server configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'mail.recaria.org')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', '587'))
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False
EMAIL_HOST_USER = os.environ.get('EMAIL_USER', 'berk@recaria.org')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.environ.get('EMAIL_FROM', 'berk@recaria.org')
SERVER_EMAIL = os.environ.get('SERVER_EMAIL', 'berk@recaria.org')

# Frontend URL for email links (verification, password reset, etc.)
FRONTEND_URL = os.environ.get('FRONTEND_URL', 'https://recaria.org')

# Logging - Production server
# Log files stored in data/logs directory (created by deploy)
LOG_DIR = Path(os.environ.get('LOG_DIR', str(DATA_DIR / 'logs')))
LOG_DIR.mkdir(parents=True, exist_ok=True)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{levelname}] {asctime} {name} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': str(LOG_DIR / 'django.log'),
            'maxBytes': 1024 * 1024 * 10,  # 10MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
        'unibos': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# UNIBOS Hub-specific settings
UNIBOS_DEPLOYMENT_TYPE = 'hub'  # hub, node, worker, dev
UNIBOS_IDENTITY_PROVIDER = True  # This is the identity provider
UNIBOS_NODE_REGISTRY_ENABLED = True  # Enable node coordination
UNIBOS_SYNC_HUB_ENABLED = True  # Enable central sync hub
UNIBOS_P2P_ENABLED = False  # Hub doesn't participate in P2P mesh
UNIBOS_OFFLINE_MODE = False  # Hub is always online

# Performance monitoring
# Disable prometheus auto-export to avoid port conflicts during migrations
# Metrics will be served via /metrics endpoint instead
PROMETHEUS_METRICS_EXPORT_PORT = None
PROMETHEUS_METRICS_EXPORT_ADDRESS = None
