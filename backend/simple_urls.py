
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
