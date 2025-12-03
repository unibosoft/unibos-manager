"""
UNIBOS Edge Node Settings
Raspberry Pi and local edge device deployment

This settings file is optimized for edge devices:
- Local-first data storage (privacy)
- Minimal resource usage (Pi Zero 2W compatible)
- SQLite fallback when PostgreSQL unavailable
- Optional Redis (file-based cache fallback)
- Selective module loading based on device capabilities
- mDNS discovery support
- Offline-capable operation
"""

import os
import socket
from pathlib import Path

# Import base settings
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Import all base settings
from .base import *

# =============================================================================
# CORE SETTINGS
# =============================================================================

DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'

# Get hostname and local IP for allowed hosts
HOSTNAME = socket.gethostname()
try:
    LOCAL_IP = socket.gethostbyname(HOSTNAME)
except socket.gaierror:
    LOCAL_IP = '127.0.0.1'

ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    HOSTNAME,
    f'{HOSTNAME}.local',  # mDNS
    LOCAL_IP,
    os.environ.get('ALLOWED_HOST', '*'),
]

# Allow all hosts in edge mode for local network access
if os.environ.get('ALLOW_ALL_HOSTS', 'true').lower() == 'true':
    ALLOWED_HOSTS = ['*']

# =============================================================================
# DATABASE - Local PostgreSQL or SQLite Fallback
# =============================================================================

# Check if PostgreSQL is available
def check_postgres_available():
    """Check if PostgreSQL is running and accessible."""
    import socket
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(('localhost', 5432))
        sock.close()
        return result == 0
    except:
        return False

# Use environment variable or auto-detect
USE_POSTGRES = os.environ.get('USE_POSTGRES', 'auto')
if USE_POSTGRES == 'auto':
    USE_POSTGRES = check_postgres_available()
else:
    USE_POSTGRES = USE_POSTGRES.lower() == 'true'

if USE_POSTGRES:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.environ.get('DB_NAME', 'unibos_db'),
            'USER': os.environ.get('DB_USER', 'unibos_user'),
            'PASSWORD': os.environ.get('DB_PASS', ''),
            'HOST': os.environ.get('DB_HOST', 'localhost'),
            'PORT': os.environ.get('DB_PORT', '5432'),
            'OPTIONS': {
                'connect_timeout': 5,
            },
            'CONN_MAX_AGE': 60,  # Lower connection pooling for edge
        }
    }
else:
    # SQLite fallback for minimal installations
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR.parent.parent.parent / 'data' / 'db' / 'unibos.sqlite3',
            'OPTIONS': {
                'timeout': 20,
            }
        }
    }
    # Ensure SQLite directory exists
    DATABASES['default']['NAME'].parent.mkdir(parents=True, exist_ok=True)

# =============================================================================
# CACHE - Redis or File-based Fallback
# =============================================================================

def check_redis_available():
    """Check if Redis is running and accessible."""
    import socket
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(('localhost', 6379))
        sock.close()
        return result == 0
    except:
        return False

USE_REDIS = os.environ.get('USE_REDIS', 'auto')
if USE_REDIS == 'auto':
    USE_REDIS = check_redis_available()
else:
    USE_REDIS = USE_REDIS.lower() == 'true'

if USE_REDIS:
    REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
    CACHES = {
        'default': {
            'BACKEND': 'django_redis.cache.RedisCache',
            'LOCATION': REDIS_URL,
            'OPTIONS': {
                'CLIENT_CLASS': 'django_redis.client.DefaultClient',
                'SOCKET_CONNECT_TIMEOUT': 2,
                'SOCKET_TIMEOUT': 2,
                'CONNECTION_POOL_KWARGS': {
                    'max_connections': 10,  # Lower for edge
                }
            },
            'KEY_PREFIX': 'unibos_edge',
            'TIMEOUT': 300,
        }
    }
    SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
else:
    # File-based cache fallback
    CACHE_DIR = BASE_DIR.parent.parent.parent / 'data' / 'cache'
    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
            'LOCATION': str(CACHE_DIR),
            'TIMEOUT': 300,
            'OPTIONS': {
                'MAX_ENTRIES': 1000
            }
        }
    }
    SESSION_ENGINE = 'django.contrib.sessions.backends.db'

# =============================================================================
# CELERY - Optional for Edge
# =============================================================================

CELERY_ENABLED = os.environ.get('CELERY_ENABLED', 'auto')
if CELERY_ENABLED == 'auto':
    CELERY_ENABLED = USE_REDIS  # Only enable if Redis is available
else:
    CELERY_ENABLED = CELERY_ENABLED.lower() == 'true'

if CELERY_ENABLED and USE_REDIS:
    CELERY_BROKER_URL = REDIS_URL
    CELERY_RESULT_BACKEND = REDIS_URL
    CELERY_TASK_ALWAYS_EAGER = False
else:
    # Run tasks synchronously without Celery
    CELERY_TASK_ALWAYS_EAGER = True
    CELERY_TASK_EAGER_PROPAGATES = True

CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Europe/Istanbul'

# Reduced worker settings for edge
CELERY_WORKER_CONCURRENCY = int(os.environ.get('CELERY_CONCURRENCY', '2'))
CELERY_TASK_TIME_LIMIT = 10 * 60  # 10 minutes max for edge

# =============================================================================
# SECURITY
# =============================================================================

SECRET_KEY = os.environ.get('SECRET_KEY', 'edge-node-secret-key-please-change-in-production')

# Edge nodes typically don't use HTTPS (behind local network)
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = False
SESSION_COOKIE_SAMESITE = 'Lax'

# CSRF trusted origins for local network
CSRF_TRUSTED_ORIGINS = [
    f'http://{HOSTNAME}:8000',
    f'http://{HOSTNAME}.local:8000',
    f'http://{LOCAL_IP}:8000',
    'http://localhost:8000',
    'http://127.0.0.1:8000',
]

# Add any custom origins from environment
CUSTOM_ORIGINS = os.environ.get('CSRF_ORIGINS', '')
if CUSTOM_ORIGINS:
    CSRF_TRUSTED_ORIGINS.extend(CUSTOM_ORIGINS.split(','))

# =============================================================================
# STATIC & MEDIA FILES
# =============================================================================

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media files - Local storage
DATA_DIR = BASE_DIR.parent.parent.parent / 'data'
MEDIA_URL = '/media/'
MEDIA_ROOT = DATA_DIR / 'media'
MEDIA_ROOT.mkdir(parents=True, exist_ok=True)

# =============================================================================
# LOGGING - Minimal for Edge
# =============================================================================

LOG_DIR = DATA_DIR / 'logs'
LOG_DIR.mkdir(parents=True, exist_ok=True)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {
            'format': '[{levelname}] {asctime} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'WARNING',  # Only warnings and errors to save disk
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': str(LOG_DIR / 'unibos.log'),
            'maxBytes': 1024 * 1024 * 5,  # 5MB (smaller for SD card)
            'backupCount': 2,
            'formatter': 'simple',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'WARNING',
            'propagate': False,
        },
    },
}

# =============================================================================
# MODULE CONFIGURATION - Selective Loading
# =============================================================================

# Get enabled modules from environment or use defaults based on resources
ENABLED_MODULES = os.environ.get('ENABLED_MODULES', '')

if ENABLED_MODULES:
    ENABLED_MODULES = [m.strip() for m in ENABLED_MODULES.split(',') if m.strip()]
else:
    # Auto-detect based on available memory
    try:
        with open('/proc/meminfo', 'r') as f:
            meminfo = f.read()
            mem_total = int([l for l in meminfo.split('\n') if 'MemTotal' in l][0].split()[1])
            mem_mb = mem_total // 1024
    except:
        mem_mb = 4096  # Default to 4GB if can't detect

    if mem_mb < 1024:  # < 1GB (Pi Zero 2W)
        ENABLED_MODULES = ['wimm']
    elif mem_mb < 2048:  # < 2GB
        ENABLED_MODULES = ['wimm', 'documents']
    elif mem_mb < 4096:  # < 4GB
        ENABLED_MODULES = ['wimm', 'documents', 'personal_inflation', 'wims']
    else:  # >= 4GB
        ENABLED_MODULES = 'all'  # All modules

# =============================================================================
# EDGE-SPECIFIC SETTINGS
# =============================================================================

# Node identity
UNIBOS_DEPLOYMENT_TYPE = 'edge'
UNIBOS_NODE_TYPE = os.environ.get('NODE_TYPE', 'edge')
UNIBOS_PLATFORM = os.environ.get('NODE_PLATFORM', 'linux')
UNIBOS_PLATFORM_DETAIL = os.environ.get('NODE_PLATFORM_DETAIL', 'unknown')

# Central registry for node discovery
CENTRAL_REGISTRY_URL = os.environ.get('CENTRAL_REGISTRY_URL', 'https://unibos.recaria.org')

# Sync settings
UNIBOS_SYNC_ENABLED = os.environ.get('SYNC_ENABLED', 'false').lower() == 'true'
UNIBOS_SYNC_INTERVAL = int(os.environ.get('SYNC_INTERVAL', '300'))  # 5 minutes

# Privacy settings - Edge nodes keep data local by default
UNIBOS_LOCAL_ONLY_MODULES = ['wimm', 'documents', 'cctv', 'personal_inflation']
UNIBOS_SYNC_ALLOWED_MODULES = ['currencies', 'birlikteyiz']  # Only price/alert data

# mDNS settings
UNIBOS_MDNS_ENABLED = os.environ.get('MDNS_ENABLED', 'true').lower() == 'true'
UNIBOS_MDNS_SERVICE_TYPE = '_unibos._tcp.local.'
UNIBOS_MDNS_SERVICE_PORT = int(os.environ.get('SERVICE_PORT', '8000'))

# Offline mode - Edge nodes can work without internet
UNIBOS_OFFLINE_MODE = True
UNIBOS_OFFLINE_QUEUE_ENABLED = True

# =============================================================================
# PERFORMANCE OPTIMIZATIONS
# =============================================================================

# Reduce memory usage
DATA_UPLOAD_MAX_MEMORY_SIZE = 5 * 1024 * 1024  # 5MB max upload
FILE_UPLOAD_MAX_MEMORY_SIZE = 2 * 1024 * 1024  # 2MB in memory

# Disable some middleware for performance
MIDDLEWARE = [m for m in MIDDLEWARE if 'prometheus' not in m.lower()]

# Disable Prometheus for edge (unless explicitly enabled)
if not os.environ.get('PROMETHEUS_ENABLED', 'false').lower() == 'true':
    INSTALLED_APPS = [app for app in INSTALLED_APPS if 'prometheus' not in app]

# Print configuration summary on startup
print(f"🍓 Edge settings loaded")
print(f"   Platform: {UNIBOS_PLATFORM} ({UNIBOS_PLATFORM_DETAIL})")
print(f"   Database: {'PostgreSQL' if USE_POSTGRES else 'SQLite'}")
print(f"   Cache: {'Redis' if USE_REDIS else 'File-based'}")
print(f"   Celery: {'Enabled' if CELERY_ENABLED else 'Disabled (sync mode)'}")
print(f"   Modules: {ENABLED_MODULES}")
print(f"   mDNS: {'Enabled' if UNIBOS_MDNS_ENABLED else 'Disabled'}")
