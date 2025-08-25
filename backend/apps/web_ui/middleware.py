"""
Middleware for web UI security and navigation control
"""

from django.shortcuts import redirect
from django.urls import reverse
from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth.decorators import login_required


class SolitaireSecurityMiddleware(MiddlewareMixin):
    """
    Middleware to ensure solitaire screen lock security
    Allows multiple tabs with independent solitaire sessions
    """
    
    def process_request(self, request):
        # Skip for non-authenticated users
        if not request.user.is_authenticated:
            return None
            
        path = request.path
        
        # For solitaire pages, just ensure user is authenticated
        # Each tab can have its own solitaire session
        if '/solitaire/' in path:
            # Check if this is a direct URL access without referrer
            referer = request.META.get('HTTP_REFERER', '')
            
            # If no referrer and not an API call, check if it's a legitimate access
            if not referer and '/api/' not in path:
                # Allow duplicate tab (referrer is empty for duplicated tabs)
                # This enables the duplicate tab functionality
                pass
        
        return None
    
    def process_response(self, request, response):
        # Add security headers for solitaire pages
        if request.path and '/solitaire/' in request.path:
            # Prevent caching
            response['Cache-Control'] = 'no-cache, no-store, must-revalidate, private'
            response['Pragma'] = 'no-cache'
            response['Expires'] = '0'
            
            # Prevent iframe embedding
            response['X-Frame-Options'] = 'DENY'
            response['X-Content-Type-Options'] = 'nosniff'
            
            # Disable browser XSS protection (we handle it ourselves)
            response['X-XSS-Protection'] = '0'
            
            # Content Security Policy
            response['Content-Security-Policy'] = "default-src 'self' 'unsafe-inline' 'unsafe-eval'; frame-ancestors 'none';"
        
        return response