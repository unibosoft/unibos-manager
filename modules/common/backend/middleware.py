"""
Custom middleware for UNIBOS backend
Implements security headers, rate limiting, and request logging
"""

import time
import json
import logging
from typing import Callable
from django.core.cache import cache
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from modules.authentication.backend.models import UserSession

logger = logging.getLogger(__name__)


class SecurityHeadersMiddleware(MiddlewareMixin):
    """Add security headers to all responses"""
    
    def process_response(self, request, response):
        # Security headers
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
        
        # HSTS is handled by Django's SecurityMiddleware in production
        
        # CSP headers (if not in debug mode)
        if not settings.DEBUG:
            csp_directives = [
                "default-src 'self'",
                "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net https://unpkg.com",
                "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://unpkg.com",
                "font-src 'self' https://fonts.gstatic.com",
                "img-src 'self' data: https:",
                "connect-src 'self' wss: https:",
                "frame-ancestors 'none'",
                "base-uri 'self'",
                "form-action 'self'",
            ]
            response['Content-Security-Policy'] = '; '.join(csp_directives)
        
        return response


class RequestLoggingMiddleware(MiddlewareMixin):
    """Log all requests for monitoring and debugging"""
    
    def process_request(self, request):
        request.start_time = time.time()
        
        # Log request
        logger.info(
            "Request started",
            extra={
                'method': request.method,
                'path': request.path,
                'user': getattr(request.user, 'username', 'anonymous'),
                'ip': self.get_client_ip(request),
                'user_agent': request.META.get('HTTP_USER_AGENT', ''),
            }
        )
    
    def process_response(self, request, response):
        # Calculate request duration
        if hasattr(request, 'start_time'):
            duration = time.time() - request.start_time
            
            # Log response
            logger.info(
                "Request completed",
                extra={
                    'method': request.method,
                    'path': request.path,
                    'status': response.status_code,
                    'duration': f"{duration:.3f}s",
                    'user': getattr(request.user, 'username', 'anonymous'),
                }
            )
            
            # Add timing header
            response['X-Response-Time'] = f"{duration:.3f}s"
        
        return response
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class RateLimitMiddleware(MiddlewareMixin):
    """Global rate limiting middleware"""
    
    def process_request(self, request):
        # Skip rate limiting for certain paths
        exempt_paths = ['/admin/', '/static/', '/media/', '/health/', '/administration/unlock/', '/birlikteyiz/']
        if any(request.path.startswith(path) for path in exempt_paths):
            return None
        
        # Get client identifier
        if request.user.is_authenticated:
            identifier = f"user_{request.user.id}"
            limit = 50000  # Authenticated users: 50000 requests per hour
        else:
            identifier = f"ip_{self.get_client_ip(request)}"
            limit = 10000  # Anonymous users: 10000 requests per hour
        
        # Check rate limit
        cache_key = f"rate_limit_{identifier}"
        requests_count = cache.get(cache_key, 0)
        
        if requests_count >= limit:
            return JsonResponse(
                {
                    'error': 'Rate limit exceeded',
                    'detail': f'Too many requests. Limit: {limit} requests per hour.'
                },
                status=429
            )
        
        # Increment counter
        cache.set(cache_key, requests_count + 1, 3600)  # 1 hour TTL
        
        return None
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class JWTAuthMiddleware:
    """JWT authentication for WebSocket connections"""
    
    def __init__(self, inner):
        self.inner = inner
    
    async def __call__(self, scope, receive, send):
        # Get token from query string or headers
        headers = dict(scope.get('headers', []))
        
        # Try to get token from Authorization header
        auth_header = headers.get(b'authorization', b'').decode()
        if auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
        else:
            # Try to get token from query string
            query_string = scope.get('query_string', b'').decode()
            params = dict(param.split('=') for param in query_string.split('&') if '=' in param)
            token = params.get('token', None)
        
        if token:
            try:
                # Validate token
                jwt_auth = JWTAuthentication()
                validated_token = jwt_auth.get_validated_token(token)
                user = await database_sync_to_async(jwt_auth.get_user)(validated_token)
                
                # Update session activity
                session_key = validated_token.get('jti')
                if session_key:
                    await database_sync_to_async(self.update_session_activity)(user, session_key)
                
                # Add user to scope
                scope['user'] = user
            except (InvalidToken, TokenError) as e:
                # Invalid token, set anonymous user
                scope['user'] = AnonymousUser()
        else:
            # No token provided
            scope['user'] = AnonymousUser()
        
        return await self.inner(scope, receive, send)
    
    def update_session_activity(self, user, session_key):
        """Update session last activity"""
        try:
            session = UserSession.objects.get(
                user=user,
                session_key=session_key,
                is_active=True
            )
            session.save(update_fields=['last_activity'])
        except UserSession.DoesNotExist:
            pass


class CorsMiddleware(MiddlewareMixin):
    """Custom CORS middleware for fine-grained control"""
    
    def process_response(self, request, response):
        # This is handled by django-cors-headers, but we can add custom logic here
        # For WebSocket support
        if request.path.startswith('/ws/'):
            origin = request.META.get('HTTP_ORIGIN')
            if origin in settings.CORS_ALLOWED_ORIGINS:
                response['Access-Control-Allow-Origin'] = origin
                response['Access-Control-Allow-Credentials'] = 'true'
        
        return response


class HealthCheckMiddleware(MiddlewareMixin):
    """Quick health check middleware"""
    
    def process_request(self, request):
        if request.path == '/health/quick/':
            return JsonResponse({'status': 'ok', 'timestamp': time.time()})
        return None