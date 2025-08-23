#!/usr/bin/env python
"""
Simple Django server runner
Runs a minimal Django server without complex dependencies
"""

import os
import sys
import django
from django.conf import settings
from django.core.management import execute_from_command_line

# Configure Django with minimal settings
settings.configure(
    DEBUG=True,
    SECRET_KEY='dev-key-for-testing-only',
    ROOT_URLCONF='simple_urls',
    ALLOWED_HOSTS=['*'],
    INSTALLED_APPS=[
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.messages',
        'django.contrib.staticfiles',
    ],
    MIDDLEWARE=[
        'django.middleware.security.SecurityMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.common.CommonMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        'django.middleware.clickjacking.XFrameOptionsMiddleware',
    ],
    DATABASES={
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': 'db.sqlite3',
        }
    },
    STATIC_URL='/static/',
    TEMPLATES=[{
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    }],
)

# Setup Django
django.setup()

# Create simple URLs module
with open('simple_urls.py', 'w') as f:
    f.write("""
from django.urls import path
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

def health_check(request):
    return JsonResponse({
        'status': 'ok',
        'message': 'UNIBOS Web Server is running!',
        'version': 'v510'
    })

def home(request):
    return JsonResponse({
        'welcome': 'UNIBOS Web Interface',
        'endpoints': {
            '/': 'This page',
            '/health/': 'Health check',
            '/api/': 'API endpoint'
        }
    })

@csrf_exempt
def api_endpoint(request):
    return JsonResponse({
        'message': 'API is working!',
        'method': request.method,
        'path': request.path
    })

urlpatterns = [
    path('', home),
    path('health/', health_check),
    path('api/', api_endpoint),
]
""")

# Run the server
if __name__ == '__main__':
    execute_from_command_line(['manage.py', 'runserver', '0.0.0.0:8000'])