"""
Activity tracking middleware for UNIBOS
Updates user's last_activity field intelligently
"""

from django.utils import timezone
from django.core.cache import cache
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)


class UserActivityMiddleware:
    """
    Middleware to track user activity with intelligent updates.
    Only updates database every 5 minutes per user to avoid performance issues.
    """
    
    # Update interval in seconds (5 minutes)
    UPDATE_INTERVAL = 300
    
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        # Process the request
        response = self.get_response(request)
        
        # Update activity after response to avoid blocking
        if request.user.is_authenticated:
            self.update_user_activity(request.user)
            
        return response
    
    def update_user_activity(self, user):
        """
        Update user's last activity timestamp intelligently.
        Uses cache to avoid frequent database writes.
        """
        try:
            # Cache key for this user's last update
            cache_key = f'user_activity_updated_{user.id}'
            
            # Check if we've recently updated this user's activity
            last_update = cache.get(cache_key)
            
            if not last_update:
                # No recent update, update now
                user.last_activity = timezone.now()
                user.save(update_fields=['last_activity'])
                
                # Store in cache to prevent frequent updates
                cache.set(cache_key, True, self.UPDATE_INTERVAL)
                
                logger.debug(f"Updated activity for user {user.username}")
            else:
                # Recently updated, skip database write
                logger.debug(f"Skipped activity update for user {user.username} (cached)")
                
        except Exception as e:
            # Don't let activity tracking errors break the application
            logger.error(f"Error updating user activity: {e}")


class APIActivityMiddleware:
    """
    Lightweight activity tracking for API endpoints.
    Only tracks activity for authenticated API requests.
    """
    
    # Update interval for API requests (10 minutes)
    UPDATE_INTERVAL = 600
    
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        response = self.get_response(request)
        
        # Only track for API endpoints
        if request.path.startswith('/api/') and hasattr(request, 'user') and request.user.is_authenticated:
            self.update_api_activity(request.user)
            
        return response
    
    def update_api_activity(self, user):
        """
        Update activity for API requests with longer cache interval.
        """
        try:
            cache_key = f'api_activity_updated_{user.id}'
            
            if not cache.get(cache_key):
                # Update last_activity
                user.last_activity = timezone.now()
                user.save(update_fields=['last_activity'])
                
                # Cache for longer period for API requests
                cache.set(cache_key, True, self.UPDATE_INTERVAL)
                
                logger.debug(f"Updated API activity for user {user.username}")
                
        except Exception as e:
            logger.error(f"Error updating API activity: {e}")