"""
Development settings without Redis dependency
Use this for quick development without Redis, Celery, or WebSockets
"""
from .base import *

# Use simple URLs without drf_spectacular
ROOT_URLCONF = 'unibos_backend.urls_simple'

# Override cache to use local memory instead of Redis
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
        'TIMEOUT': 300,  # 5 minutes
        'OPTIONS': {
            'MAX_ENTRIES': 1000,
        }
    }
}

# Use database sessions instead of cache-based sessions
SESSION_ENGINE = 'django.contrib.sessions.backends.db'

# Disable Channels (WebSocket support) since it requires Redis
# Remove channels from INSTALLED_APPS if it exists
INSTALLED_APPS = [app for app in INSTALLED_APPS if app != 'channels']

# Remove Channels middleware if present
if 'channels.middleware.AsgiHandler' in MIDDLEWARE:
    MIDDLEWARE = [m for m in MIDDLEWARE if 'channels' not in m]

# No WebSocket support without Redis
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer'
    }
}

# Celery configuration - use eager mode for development without Redis
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True
CELERY_BROKER_URL = 'memory://'
CELERY_RESULT_BACKEND = 'cache+memory://'

# Remove any Redis-dependent and missing apps from INSTALLED_APPS
APPS_TO_REMOVE = [
    'django_celery_beat',
    'health_check.contrib.redis',
    'django_prometheus',
    'django_filters',
    'drf_spectacular',
    'django_extensions',
    'whitenoise',
    'modules.authentication.backend',
    'modules.users.backend',
    'modules.currencies.backend',
    'modules.personal_inflation.backend',
    'modules.recaria.backend',
    'modules.birlikteyiz.backend',
    'core.system.common.backend',
]

# Basic Django apps only
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
]

# Simplified middleware without missing components
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Simplified WSGI application (no ASGI/WebSockets)
WSGI_APPLICATION = 'unibos_backend.wsgi.application'

# Development-specific settings
DEBUG = True
ALLOWED_HOSTS = ['*']

# Use default Django user model since custom app is not available
AUTH_USER_MODEL = 'auth.User'

# Disable some production features
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

print("=" * 50)
print("Running with dev_no_redis settings:")
print("- Cache: Local Memory")
print("- Sessions: Database")
print("- WebSockets: Disabled")
print("- Celery: Eager mode (synchronous)")
print("- Redis: Not required")
print("=" * 50)