"""
UNIBOS Backend Base Settings
Secure, scalable Django configuration for production use
"""

import sys
import os
from pathlib import Path

# Add UNIBOS root directory to Python path so modules/ can be imported
# This file is in: platform/runtime/web/backend/unibos_backend/settings/base.py
# Path: base.py → settings/ → unibos_backend/ → backend/ → web/ → runtime/ → core/ → (UNIBOS root)
# UNIBOS root is 7 levels up
_unibos_root = Path(__file__).resolve().parent.parent.parent.parent.parent.parent.parent
if str(_unibos_root) not in sys.path:
    sys.path.insert(0, str(_unibos_root))
from datetime import timedelta
import environ

# Build paths inside the project
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Environment variables
env = environ.Env(
    DEBUG=(bool, False),
    ALLOWED_HOSTS=(list, []),
    DATABASE_URL=(str, 'postgresql://unibos:unibos@localhost:5432/unibos'),
    REDIS_URL=(str, 'redis://localhost:6379/0'),
    SECRET_KEY=(str, None),
)

# Read .env file
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY')
if not SECRET_KEY:
    raise ValueError("SECRET_KEY environment variable is not set")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env('DEBUG')

ALLOWED_HOSTS = env('ALLOWED_HOSTS')

# Application definition
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.postgres',  # PostgreSQL specific features
]

THIRD_PARTY_APPS = [
    'rest_framework',
    'rest_framework.authtoken',  # Token authentication support
    'rest_framework_simplejwt',
    'corsheaders',
    'django_filters',
    'channels',
    'django_prometheus',
    'drf_spectacular',
    'django_extensions',
    'django_celery_beat',  # Celery Beat database scheduler
]

CORE_APPS = [
    'modules.core.backend',  # Core models - MUST be first (MIGRATED from apps.core)
]

UNIBOS_SYSTEM_APPS = [
    # Module registry must be loaded early to discover modules
    # Note: module_registry was removed during v533 architectural migration
    # TODO: Implement new module discovery system
    # 'core.backend.core_apps.module_registry',  # UNIBOS Module Registry (DEPRECATED)
]

UNIBOS_MODULES = [
    # New modular architecture - modules from modules/ directory
    'modules.birlikteyiz.backend',  # Emergency mesh network (reference implementation)
    'modules.documents.backend',  # OCR and document management system
    'modules.currencies.backend',  # Currency tracking and portfolio management
    'modules.personal_inflation.backend',  # Personal inflation tracking
    'modules.recaria.backend',  # Medieval consciousness exploration MMORPG
    'modules.cctv.backend',  # Security camera management system
    'modules.movies.backend',  # Movie and TV series collection
    'modules.music.backend',  # Music collection with Spotify integration
    'modules.restopos.backend',  # Restaurant POS system
    'modules.wimm.backend',  # Where Is My Money - Personal finance tracker
    'modules.wims.backend',  # Where Is My Stuff - Inventory management
    'modules.solitaire.backend',  # Solitaire game with session tracking
    'modules.version_manager.backend',  # Version archive management
    'modules.administration.backend',  # Administration module for user/role management
    'modules.logging.backend',  # System and activity logging
]

LOCAL_APPS = [
    # All apps migrated to modules/ structure
    'modules.authentication.backend',  # MIGRATED from apps.authentication
    'modules.users.backend',  # Custom User model with UUID - MIGRATED from apps.users
    'modules.common.backend',  # MIGRATED from apps.common
    'modules.web_ui.backend',  # MIGRATED from apps.web_ui
    'modules.store.backend',  # Store - Marketplace Integration & Order Management - MIGRATED from store

    # === ALL APPS SUCCESSFULLY MIGRATED TO MODULES/ ===
    # 'apps.core',  # MIGRATED to modules/core/
    # 'apps.authentication',  # MIGRATED to modules/authentication/
    # 'apps.users',  # MIGRATED to modules/users/
    # 'apps.common',  # MIGRATED to modules/common/
    # 'apps.web_ui',  # MIGRATED to modules/web_ui/
    # 'store',  # MIGRATED to modules/store/
    # 'apps.currencies',  # MIGRATED to modules/currencies/
    # 'apps.personal_inflation',  # MIGRATED to modules/personal_inflation/
    # 'apps.recaria',  # MIGRATED to modules/recaria/
    # 'apps.birlikteyiz',  # MIGRATED to modules/birlikteyiz/
    # 'apps.cctv',  # MIGRATED to modules/cctv/
    # 'apps.documents',  # MIGRATED to modules/documents/
    # 'apps.version_manager',  # MIGRATED to modules/version_manager/
    # 'apps.administration',  # MIGRATED to modules/administration/
    # 'apps.solitaire',  # MIGRATED to modules/solitaire/
    # 'apps.movies',  # MIGRATED to modules/movies/
    # 'apps.music',  # MIGRATED to modules/music/
    # 'apps.restopos',  # MIGRATED to modules/restopos/
    # 'apps.wimm',  # MIGRATED to modules/wimm/
    # 'apps.wims',  # MIGRATED to modules/wims/
    # 'apps.logging',  # MIGRATED to modules/logging/
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + CORE_APPS + UNIBOS_SYSTEM_APPS + UNIBOS_MODULES + LOCAL_APPS

MIDDLEWARE = [
    'django_prometheus.middleware.PrometheusBeforeMiddleware',  # Must be first
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',  # Added for admin
    'corsheaders.middleware.CorsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'modules.common.backend.middleware.SecurityHeadersMiddleware',
    'modules.common.backend.middleware.RequestLoggingMiddleware',
    'modules.common.backend.middleware.RateLimitMiddleware',
    'modules.web_ui.backend.middleware.SolitaireSecurityMiddleware',  # Solitaire screen lock security
    'modules.web_ui.backend.middleware_navigation.NavigationTrackingMiddleware',  # Track last visited page
    'modules.common.backend.middleware_activity.UserActivityMiddleware',  # Track user activity
    'modules.common.backend.middleware_activity.APIActivityMiddleware',  # Track API activity
    'modules.logging.backend.middleware.SystemLoggingMiddleware',  # System logging
    'modules.logging.backend.middleware.ActivityLoggingMiddleware',  # Activity logging
    'django_prometheus.middleware.PrometheusAfterMiddleware',  # Must be last
]

ROOT_URLCONF = 'unibos_backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                # UNIBOS custom context processors
                'modules.web_ui.backend.context_processors.sidebar_context',
                'modules.web_ui.backend.context_processors.version_context',
                'modules.web_ui.backend.context_processors.unibos_context',
            ],
        },
    },
]

# ASGI Configuration for WebSocket support
ASGI_APPLICATION = 'unibos_backend.asgi.application'

# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases
DATABASES = {
    'default': env.db(),
}

# PostgreSQL connection pooling
DATABASES['default']['CONN_MAX_AGE'] = 60
DATABASES['default']['OPTIONS'] = {
    'connect_timeout': 10,
    'options': '-c statement_timeout=30000',  # 30 seconds
}

# Redis Configuration
REDIS_URL = env('REDIS_URL')

# Cache Configuration
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': REDIS_URL,
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'CONNECTION_POOL_KWARGS': {
                'max_connections': 50,
                'retry_on_timeout': True,
            },
            'SOCKET_CONNECT_TIMEOUT': 5,
            'SOCKET_TIMEOUT': 5,
            'COMPRESSOR': 'django_redis.compressors.zlib.ZlibCompressor',
            'IGNORE_EXCEPTIONS': True,
        },
        'KEY_PREFIX': 'unibos',
        'TIMEOUT': 300,  # 5 minutes default
    }
}

# Session Configuration
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'
SESSION_COOKIE_AGE = 86400  # 24 hours
SESSION_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 10,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
    {
        'NAME': 'modules.authentication.backend.validators.CustomPasswordValidator',
    },
]

# Custom User Model
AUTH_USER_MODEL = 'users.User'  # Custom User model with UUID

# Authentication URLs
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/login/'

# Internationalization
LANGUAGE_CODE = 'tr-tr'
TIME_ZONE = 'Europe/Istanbul'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# Media files - Universal Data Directory
# All media files stored in centralized /data directory structure
MEDIA_URL = '/media/'
DATA_DIR = BASE_DIR.parent.parent.parent / 'data'
MEDIA_ROOT = DATA_DIR / 'runtime' / 'media'

# UNIBOS Module System Configuration
# Project root directory (contains modules/, core/, shared/)
PROJECT_ROOT = BASE_DIR.parent.parent.parent
MODULES_DIR = PROJECT_ROOT / 'modules'

# Add UNIBOS project root to Python path (for core/ and modules/ imports)
import sys
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Add shared Python SDK to path for UNIBOS modules
SDK_PATH = PROJECT_ROOT / 'shared' / 'python'
if SDK_PATH.exists() and str(SDK_PATH) not in sys.path:
    sys.path.insert(0, str(SDK_PATH))

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# REST Framework Configuration
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.MultiPartParser',
    ],
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_PAGINATION_CLASS': 'modules.common.backend.pagination.StandardResultsSetPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'EXCEPTION_HANDLER': 'modules.common.backend.exceptions.custom_exception_handler',
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour',
        'burst': '60/minute',
    },
    'DATETIME_FORMAT': '%Y-%m-%d %H:%M:%S',
    'DATE_FORMAT': '%Y-%m-%d',
}

# JWT Configuration
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=30),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
    'JTI_CLAIM': 'jti',
    'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
    'SLIDING_TOKEN_LIFETIME': timedelta(minutes=5),
    'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=1),
}

# CORS Configuration
CORS_ALLOWED_ORIGINS = env.list('CORS_ALLOWED_ORIGINS', default=[])
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

# Channels Configuration
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [REDIS_URL],
            'capacity': 1500,
            'expiry': 10,
        },
    },
}

# Celery Configuration
CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = REDIS_URL
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60  # 30 minutes
CELERY_TASK_SOFT_TIME_LIMIT = 25 * 60  # 25 minutes
CELERY_WORKER_PREFETCH_MULTIPLIER = 4
CELERY_WORKER_MAX_TASKS_PER_CHILD = 1000

# Celery Beat Schedule
CELERY_BEAT_SCHEDULE = {
    'cleanup-expired-tokens': {
        'task': 'modules.authentication.backend.tasks.cleanup_expired_tokens',
        'schedule': timedelta(hours=24),
    },
    'update-currency-rates': {
        'task': 'modules.currencies.backend.tasks.update_currency_rates',
        'schedule': timedelta(minutes=30),
    },
    'calculate-personal-inflation': {
        'task': 'modules.personal_inflation.backend.tasks.calculate_monthly_inflation',
        'schedule': timedelta(days=1),
    },
    'import-firebase-rates-incremental': {
        'task': 'modules.currencies.backend.tasks.import_firebase_rates_incremental',
        'schedule': timedelta(minutes=5),  # Check for new rates every 5 minutes
    },
    'check-currency-alerts': {
        'task': 'modules.currencies.backend.tasks.check_currency_alerts',
        'schedule': timedelta(minutes=5),  # Check alerts every 5 minutes
    },
    'cleanup-old-bank-rates': {
        'task': 'modules.currencies.backend.tasks.cleanup_old_bank_rates',
        'schedule': timedelta(days=7),  # Weekly cleanup
    },
    'generate-market-data': {
        'task': 'modules.currencies.backend.tasks.generate_market_data',
        'schedule': timedelta(hours=1),  # Generate hourly market data
    },
    'calculate-portfolio-performance': {
        'task': 'modules.currencies.backend.tasks.calculate_portfolio_performance',
        'schedule': timedelta(minutes=15),  # Update portfolio metrics
    },
    'fetch-earthquakes': {
        'task': 'modules.birlikteyiz.backend.tasks.fetch_earthquakes',
        'schedule': timedelta(minutes=5),  # Fetch earthquake data every 5 minutes
    },
}

# Email Configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'localhost'  # Will use recaria.org mail server
EMAIL_PORT = 25
EMAIL_USE_TLS = False
EMAIL_USE_SSL = False
EMAIL_HOST_USER = 'berk@recaria.org'
EMAIL_HOST_PASSWORD = 'Recaria2025Mail!'
DEFAULT_FROM_EMAIL = 'berk@recaria.org'
SERVER_EMAIL = 'berk@recaria.org'

# Security Settings
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
CSRF_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_HTTPONLY = False  # Allow JavaScript to read the cookie for AJAX requests
CSRF_COOKIE_SAMESITE = 'Lax'

# Logging Configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'json': {
            '()': 'pythonjsonlogger.jsonlogger.JsonFormatter',
            'format': '%(asctime)s %(name)s %(levelname)s %(message)s',
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'django.log',
            'maxBytes': 1024 * 1024 * 15,  # 15MB
            'backupCount': 10,
            'formatter': 'json',
        },
        'security': {
            'level': 'WARNING',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'security.log',
            'maxBytes': 1024 * 1024 * 15,  # 15MB
            'backupCount': 10,
            'formatter': 'json',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': env('DJANGO_LOG_LEVEL', default='INFO'),
            'propagate': False,
        },
        'django.security': {
            'handlers': ['security'],
            'level': 'INFO',
            'propagate': False,
        },
        'apps': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG' if DEBUG else 'INFO',
            'propagate': False,
        },
    },
}

# API Documentation
SPECTACULAR_SETTINGS = {
    'TITLE': 'UNIBOS API',
    'DESCRIPTION': 'Secure and scalable API for UNIBOS platform',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'SCHEMA_PATH_PREFIX': r'/api/v[0-9]',
    'COMPONENT_SPLIT_REQUEST': True,
    'ENUM_NAME_OVERRIDES': {},
}

# File Upload Settings
FILE_UPLOAD_MAX_MEMORY_SIZE = 5 * 1024 * 1024  # 5MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 5 * 1024 * 1024  # 5MB

# Custom Settings
UNIBOS_VERSION = '1.0.0'
UNIBOS_ENVIRONMENT = env('ENVIRONMENT', default='development')