"""
Common error handlers for UNIBOS
"""
from django.shortcuts import render
from django.http import HttpResponse

def bad_request(request, exception):
    """Handle 400 errors"""
    return HttpResponse("Bad Request", status=400)

def permission_denied(request, exception):
    """Handle 403 errors"""
    return HttpResponse("Permission Denied", status=403)

def not_found(request, exception):
    """Handle 404 errors"""
    return HttpResponse("Not Found", status=404)

def server_error(request):
    """Handle 500 errors"""
    return HttpResponse("Server Error", status=500)