"""
Simple URL Configuration for Web Forge testing
"""
from django.contrib import admin
from django.urls import path
from django.http import JsonResponse

def health_check(request):
    """Simple health check endpoint"""
    return JsonResponse({
        'status': 'ok',
        'message': 'UNIBOS Web Forge Backend is running!',
        'version': '1.0.0'
    })

def api_info(request):
    """API information endpoint"""
    return JsonResponse({
        'name': 'UNIBOS Web Forge API',
        'version': '1.0.0',
        'endpoints': {
            'health': '/api/health/',
            'info': '/api/info/',
            'admin': '/admin/'
        }
    })

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/health/', health_check, name='health_check'),
    path('api/info/', api_info, name='api_info'),
    path('', lambda request: JsonResponse({'message': 'Welcome to UNIBOS Web Forge!'})),
]