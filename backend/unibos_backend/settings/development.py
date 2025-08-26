"""
Development settings for UNIBOS Backend
"""

from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0', '.localhost', '158.178.201.117', '10.0.0.24', 'rocksteady', 'recaria.org', 'www.recaria.org', '.recaria.org', '*']

# CORS Settings for development
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:8000",
    "http://localhost:8080",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:8000",
    "http://127.0.0.1:8080",
]

# Database
# Override with SQLite for development if needed
if env('USE_SQLITE', default=False):
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Email Backend for development
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Django Debug Toolbar (disabled - not installed)
# if DEBUG:
#     INSTALLED_APPS += ['debug_toolbar']
#     MIDDLEWARE.insert(0, 'debug_toolbar.middleware.DebugToolbarMiddleware')
#     INTERNAL_IPS = ['127.0.0.1', 'localhost']

# Disable some security features for development
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# More verbose logging for development
if 'LOGGING' in globals():
    LOGGING['loggers']['django']['level'] = 'DEBUG'
    if 'apps' in LOGGING['loggers']:
        LOGGING['loggers']['apps']['level'] = 'DEBUG'

# Celery Configuration for development
CELERY_TASK_ALWAYS_EAGER = env('CELERY_EAGER', default=False)
CELERY_TASK_EAGER_PROPAGATES = True

# Static files
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

# Development-specific apps (disabled - not installed)
# INSTALLED_APPS += [
#     'django_seed',  # For generating test data
# ]

# Disable rate limiting in development
REST_FRAMEWORK['DEFAULT_THROTTLE_RATES'] = {
    'anon': '10000/hour',
    'user': '10000/hour',
    'burst': '1000/minute',
}