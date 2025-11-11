"""
Middleware to track user navigation across unibos pages
"""
from django.utils.deprecation import MiddlewareMixin
import logging

logger = logging.getLogger(__name__)

class NavigationTrackingMiddleware(MiddlewareMixin):
    """Track the last visited non-solitaire page for return navigation"""
    
    def process_request(self, request):
        # Only track for authenticated users
        if not request.user.is_authenticated:
            return None
            
        # Skip tracking for certain paths
        skip_paths = [
            '/solitaire/',
            '/api/',
            '/static/',
            '/media/',
            '/login/',
            '/logout/',
            '/admin/',
            '/__debug__/',
            '/administration/solitaire/realtime/',  # Skip realtime API endpoints
            '/administration/solitaire/api/',  # Skip solitaire API endpoints
        ]
        
        # Check if current path should be tracked
        current_path = request.path
        should_track = True
        
        for skip_path in skip_paths:
            if current_path.startswith(skip_path):
                should_track = False
                break
        
        # Track the page if it's a regular unibos page
        if should_track and request.method == 'GET':
            full_path = request.get_full_path()  # Includes query string
            request.session['last_unibos_page'] = full_path
            
            # Log navigation for debugging
            logger.debug(f"Navigation tracked: {request.user.username} -> {full_path}")
        
        return None