"""
UNIBOS Worker Settings
Background task processing with Celery

This settings file is optimized for worker processes:
- Connects to hub's PostgreSQL database
- Redis for Celery broker and result backend
- Minimal Django features (no static files, no sessions)
- Task-specific configurations
"""

import os
from pathlib import Path

# Import base settings
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Import all base settings
from .base import *

# Workers don't need debug mode
DEBUG = False

# Workers connect to hub database
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
        'ATOMIC_REQUESTS': False,  # Workers handle their own transactions
    }
}

# Redis - Celery broker and result backend
REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': REDIS_URL,
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'SOCKET_CONNECT_TIMEOUT': 5,
            'SOCKET_TIMEOUT': 5,
        },
        'KEY_PREFIX': 'unibos_worker',
        'TIMEOUT': 300,
    }
}

# Celery - Worker configuration
CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = REDIS_URL
CELERY_TASK_ALWAYS_EAGER = False
CELERY_TASK_EAGER_PROPAGATES = False
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Europe/Istanbul'
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60  # 30 minutes max
CELERY_TASK_SOFT_TIME_LIMIT = 25 * 60  # 25 minutes soft limit
CELERY_WORKER_PREFETCH_MULTIPLIER = 1  # Disable prefetching for fair distribution
CELERY_TASK_ACKS_LATE = True  # Acknowledge after task completion

# Security - Minimal for workers
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-worker-key-change-this!')

# Logging - Worker specific
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
            'filename': str(LOG_DIR / 'worker.log'),
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
        'celery': {
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

# UNIBOS Worker-specific settings
UNIBOS_DEPLOYMENT_TYPE = 'worker'  # hub, node, worker, dev
UNIBOS_IDENTITY_PROVIDER = False
UNIBOS_NODE_REGISTRY_ENABLED = False
UNIBOS_SYNC_HUB_ENABLED = False
UNIBOS_P2P_ENABLED = False
UNIBOS_OFFLINE_MODE = False

# Worker type configuration (set via environment)
UNIBOS_WORKER_TYPE = os.environ.get('WORKER_TYPE', 'all')  # all, core, ocr, media
UNIBOS_WORKER_QUEUES = os.environ.get('WORKER_QUEUES', 'default,ocr,media').split(',')
