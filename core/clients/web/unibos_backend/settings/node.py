"""
UNIBOS Node Settings
Standalone node deployment (raspberry pi, local mac)

This settings file is optimized for standalone UNIBOS nodes:
- Local PostgreSQL database for offline operation
- Offline-first with sync queue for server coordination
- P2P mesh networking enabled
- Lightweight module subset (node-compatible only)
- Optional sync with central server when online
- Energy-efficient for Raspberry Pi deployment
"""

import os
from pathlib import Path

# Import base settings
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Import all base settings
from .base import *

# Override for node deployment
DEBUG = os.environ.get('DEBUG', 'False') == 'True'

# Node-specific allowed hosts (local network)
ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '0.0.0.0',
    '.local',  # Allow .local mDNS domains
    '*',  # For P2P mesh - nodes discover each other dynamically
]

# Database - Local PostgreSQL (offline-first)
# Each node has its own database for autonomous operation
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'unibos_node_db'),  # Local node database
        'USER': os.environ.get('DB_USER', 'unibos_node_user'),
        'PASSWORD': os.environ.get('DB_PASSWORD', 'unibos_node_password'),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
        'OPTIONS': {
            'connect_timeout': 5,
        },
        'CONN_MAX_AGE': 300,  # Shorter connection lifetime for resource conservation
        'ATOMIC_REQUESTS': True,
    }
}

# Redis - Optional (nodes can work without it)
# Use lightweight in-memory cache if Redis not available
# Check for REDIS_URL or REDIS_ENABLED
REDIS_URL = os.environ.get('REDIS_URL', '')
REDIS_AVAILABLE = bool(REDIS_URL) or os.environ.get('REDIS_ENABLED', 'False') == 'True'

if REDIS_AVAILABLE:
    if not REDIS_URL:
        REDIS_URL = 'redis://localhost:6379/0'
    CACHES = {
        'default': {
            'BACKEND': 'django_redis.cache.RedisCache',
            'LOCATION': REDIS_URL,
            'OPTIONS': {
                'CLIENT_CLASS': 'django_redis.client.DefaultClient',
                'SOCKET_CONNECT_TIMEOUT': 3,
                'SOCKET_TIMEOUT': 3,
                'CONNECTION_POOL_KWARGS': {
                    'max_connections': 10,  # Lower for node
                    'retry_on_timeout': True,
                }
            },
            'KEY_PREFIX': 'unibos_node',
            'TIMEOUT': 600,  # Longer cache for offline resilience
        }
    }
else:
    # Fallback to in-memory cache (no Redis required)
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'unibos-node-cache',
            'OPTIONS': {
                'MAX_ENTRIES': 1000,
            }
        }
    }

# Celery - Optional (lightweight async tasks)
if REDIS_AVAILABLE:
    CELERY_BROKER_URL = REDIS_URL
    CELERY_RESULT_BACKEND = REDIS_URL
    CELERY_TASK_ALWAYS_EAGER = False
else:
    # Fallback to eager mode (synchronous) without Redis
    CELERY_TASK_ALWAYS_EAGER = True
    CELERY_TASK_EAGER_PROPAGATES = True

CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Europe/Istanbul'
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 10 * 60  # 10 minutes max (shorter for nodes)
CELERY_TASK_SOFT_TIME_LIMIT = 8 * 60  # 8 minutes soft limit

# Security - Local network security
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-node-key-change-this!')
SECURE_SSL_REDIRECT = False  # Nodes use HTTP on local network
SESSION_COOKIE_SECURE = False  # Allow HTTP for local operation
CSRF_COOKIE_SECURE = False
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = False
SESSION_COOKIE_SAMESITE = 'Lax'
X_FRAME_OPTIONS = 'SAMEORIGIN'  # Allow iframe for local web UI

# CSRF - More permissive for local network
CSRF_TRUSTED_ORIGINS = [
    'http://localhost:8000',
    'http://127.0.0.1:8000',
    'http://*.local:8000',
]

# Static files - Local node
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Media files - Local storage
MEDIA_URL = '/media/'
MEDIA_ROOT = os.environ.get('MEDIA_ROOT', os.path.join(BASE_DIR, 'data', 'media'))

# Email - Optional (nodes can work offline)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'  # Console output only

# Logging - Node-friendly (minimal disk I/O for Raspberry Pi)
# Log files stored in data/logs directory
LOG_DIR = Path(os.environ.get('LOG_DIR', os.path.join(BASE_DIR.parent.parent.parent, 'data', 'logs')))
LOG_DIR.mkdir(parents=True, exist_ok=True)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {
            'format': '[{levelname}] {name} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'file': {
            'level': 'WARNING',  # Only warnings/errors to file
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': str(LOG_DIR / 'node.log'),
            'maxBytes': 1024 * 1024 * 5,  # 5MB (smaller for nodes)
            'backupCount': 2,  # Keep less history
            'formatter': 'simple',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'unibos': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# UNIBOS Node-specific settings
UNIBOS_DEPLOYMENT_TYPE = 'node'  # server, node, dev
UNIBOS_NODE_REGISTRY_ENABLED = False  # Nodes don't host registry
UNIBOS_SYNC_HUB_ENABLED = False  # Nodes are sync clients, not hubs
UNIBOS_P2P_ENABLED = True  # Enable P2P mesh networking
UNIBOS_OFFLINE_MODE = True  # Offline-first architecture

# Offline queue settings
UNIBOS_OFFLINE_QUEUE_ENABLED = True
UNIBOS_OFFLINE_QUEUE_MAX_SIZE = 10000  # Max queued operations
UNIBOS_OFFLINE_QUEUE_RETENTION_DAYS = 30  # Keep queued items for 30 days

# P2P mesh settings
UNIBOS_P2P_DISCOVERY_ENABLED = True  # Enable mDNS/UPnP peer discovery
UNIBOS_P2P_PORT = int(os.environ.get('P2P_PORT', '5555'))
UNIBOS_P2P_BROADCAST_INTERVAL = 60  # Broadcast presence every 60 seconds
UNIBOS_P2P_PEER_TIMEOUT = 180  # Consider peer offline after 3 minutes

# Server sync settings (optional - only when online)
UNIBOS_SERVER_SYNC_ENABLED = os.environ.get('SERVER_SYNC_ENABLED', 'True') == 'True'
UNIBOS_SERVER_URL = os.environ.get('SERVER_URL', 'https://recaria.org')
UNIBOS_SERVER_SYNC_INTERVAL = int(os.environ.get('SYNC_INTERVAL', '300'))  # 5 minutes
UNIBOS_SERVER_API_TOKEN = os.environ.get('SERVER_API_TOKEN', '')

# Performance - Optimized for Raspberry Pi
# Reduce worker processes and threads for resource-constrained devices
GUNICORN_WORKERS = int(os.environ.get('GUNICORN_WORKERS', '2'))  # 2 workers for Pi
GUNICORN_THREADS = int(os.environ.get('GUNICORN_THREADS', '2'))  # 2 threads per worker
GUNICORN_TIMEOUT = int(os.environ.get('GUNICORN_TIMEOUT', '60'))  # 60 seconds
