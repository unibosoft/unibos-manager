"""
Emergency Django settings - Minimal configuration to get server running
"""

import os
from pathlib import Path

# Build paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-emergency-key-replace-in-production'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

# Application definition
INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',
    'modules.core.backend',  # Core shared models
    'modules.web_ui.backend',  # UNIBOS Web UI
    'modules.currencies.backend',  # Currencies module
    'modules.wimm.backend',  # Where Is My Money - Financial Management
    'modules.wims.backend',  # Where Is My Stuff - Inventory Management
    'modules.administration.backend',  # Administration module for user/role management
    'modules.cctv.backend',  # CCTV module for camera monitoring and recording
    'modules.documents.backend',  # Documents module for OCR and cross-module integration
    'modules.personal_inflation.backend',  # Personal inflation tracking module
    'modules.version_manager.backend',  # Version archive management
    'modules.movies.backend',  # Movies/Series collection management
    'modules.music.backend',  # Music library with Spotify integration
    'modules.restopos.backend',  # Restaurant POS system
    'modules.solitaire.backend',  # Solitaire game with security features
    'modules.birlikteyiz.backend',  # Emergency response and earthquake tracking
    'modules.store.backend',  # E-commerce marketplace integration
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'unibos_backend.urls_emergency'

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

WSGI_APPLICATION = 'unibos_backend.wsgi.application'

# Database - PostgreSQL
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'unibos_db',
        'USER': 'unibos_user',
        'PASSWORD': 'unibos_password',
        'HOST': 'localhost',
        'PORT': '5432',
        'CONN_MAX_AGE': 60,
        'OPTIONS': {
            'connect_timeout': 10,
        }
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'tr'
TIME_ZONE = 'Europe/Istanbul'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
] if (BASE_DIR / 'static').exists() else []

# Media files (User uploaded content) - Universal Data Directory
MEDIA_URL = '/media/'
DATA_DIR = BASE_DIR.parent.parent.parent / 'data'
MEDIA_ROOT = DATA_DIR / 'runtime' / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# CORS settings
CORS_ALLOW_ALL_ORIGINS = True

# REST Framework settings
REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
}