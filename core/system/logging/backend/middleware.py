"""
High-performance logging middleware with async support
Uses background threads for non-blocking log writes
"""

import time
import threading
import logging
from django.utils import timezone
from django.core.cache import cache
from queue import Queue
import traceback

logger = logging.getLogger(__name__)


class AsyncLogCollector:
    """
    Asynchronous log collector using thread-safe queue
    Processes logs in background thread
    """
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.queue = Queue(maxsize=10000)
            cls._instance.running = False
            cls._instance.thread = None
        return cls._instance
    
    def start(self):
        """Start the background processing thread"""
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._process_queue, daemon=True)
            self.thread.start()
            logger.info("async log collector started")
    
    def stop(self):
        """Stop the background thread"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
    
    def add_log(self, log_type, log_data):
        """Add log to queue (non-blocking)"""
        try:
            if not self.queue.full():
                self.queue.put((log_type, log_data), block=False)
            else:
                # Queue full, log to file as fallback
                logger.warning("log queue full, dropping log entry")
        except Exception as e:
            logger.error(f"error adding log to queue: {e}")
    
    def _process_queue(self):
        """Background thread to process log queue"""
        from .models import SystemLog, ActivityLog, log_buffer
        
        batch = []
        last_flush = time.time()
        
        while self.running:
            try:
                # Collect logs for batch insert
                while not self.queue.empty() and len(batch) < 100:
                    log_type, log_data = self.queue.get(timeout=0.1)
                    batch.append((log_type, log_data))
                
                # Flush if batch is full or 5 seconds passed
                if batch and (len(batch) >= 100 or time.time() - last_flush > 5):
                    self._flush_batch(batch)
                    batch.clear()
                    last_flush = time.time()
                
                # Small sleep to prevent CPU spinning
                if self.queue.empty():
                    time.sleep(0.1)
                    
            except Exception as e:
                logger.error(f"error processing log queue: {e}")
                time.sleep(1)
    
    def _flush_batch(self, batch):
        """Flush batch of logs to database"""
        from .models import SystemLog, ActivityLog
        
        system_logs = []
        activity_logs = []
        
        for log_type, log_data in batch:
            try:
                if log_type == 'system':
                    system_logs.append(SystemLog(**log_data))
                elif log_type == 'activity':
                    activity_logs.append(ActivityLog(**log_data))
            except Exception as e:
                logger.error(f"error creating log object: {e}")
        
        # Bulk insert
        try:
            if system_logs:
                SystemLog.objects.bulk_create(system_logs, ignore_conflicts=True)
            if activity_logs:
                ActivityLog.objects.bulk_create(activity_logs, ignore_conflicts=True)
        except Exception as e:
            logger.error(f"error bulk inserting logs: {e}")


# Global collector instance
log_collector = AsyncLogCollector()


class SystemLoggingMiddleware:
    """
    Middleware for system-level logging
    Tracks all requests, errors, and performance
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        # Start async collector
        log_collector.start()
    
    def __call__(self, request):
        # Skip logging for static files and health checks
        if self._should_skip_logging(request):
            return self.get_response(request)
        
        # Start timing
        start_time = time.time()
        
        # Pre-process logging
        request._log_data = {
            'timestamp': timezone.now(),
            'ip_address': self._get_client_ip(request),
            'user_agent': request.META.get('HTTP_USER_AGENT', ''),
            'request_method': request.method,
            'request_path': request.path,
            'user': request.user if request.user.is_authenticated else None,
            'session_key': request.session.session_key if hasattr(request, 'session') else '',
        }
        
        # Process request
        response = None
        exception_occurred = False
        
        try:
            response = self.get_response(request)
        except Exception as e:
            exception_occurred = True
            self._log_exception(request, e)
            raise
        finally:
            # Calculate duration
            duration_ms = int((time.time() - start_time) * 1000)
            
            # Log the request
            if not exception_occurred and response:
                self._log_request(request, response, duration_ms)
        
        return response
    
    def _should_skip_logging(self, request):
        """Check if request should be logged"""
        skip_paths = [
            '/static/', '/media/', '/health/', '/metrics/',
            '/favicon.ico', '/robots.txt'
        ]
        return any(request.path.startswith(path) for path in skip_paths)
    
    def _get_client_ip(self, request):
        """Get real client IP from request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def _log_request(self, request, response, duration_ms):
        """Log successful request"""
        from .models import LogLevel, LogCategory
        
        # Determine log level based on response status
        if response.status_code >= 500:
            level = LogLevel.ERROR
        elif response.status_code >= 400:
            level = LogLevel.WARNING
        else:
            level = LogLevel.INFO
        
        # Determine category
        if request.path.startswith('/api/'):
            category = LogCategory.API
        elif request.path.startswith('/admin/'):
            category = LogCategory.ADMIN
        elif request.path.startswith('/auth/'):
            category = LogCategory.AUTH
        else:
            category = LogCategory.USER
        
        log_data = {
            **request._log_data,
            'level': level,
            'category': category,
            'message': f"{request.method} {request.path} - {response.status_code}",
            'module': request.resolver_match.app_name if request.resolver_match else '',
            'function': request.resolver_match.view_name if request.resolver_match else '',
            'duration_ms': duration_ms,
            'extra_data': {
                'status_code': response.status_code,
                'content_type': response.get('Content-Type', ''),
            }
        }
        
        # Add to async queue
        log_collector.add_log('system', log_data)
    
    def _log_exception(self, request, exception):
        """Log exception"""
        from .models import LogLevel, LogCategory
        
        log_data = {
            **request._log_data,
            'level': LogLevel.ERROR,
            'category': LogCategory.SYSTEM,
            'message': f"Exception in {request.method} {request.path}: {str(exception)}",
            'exception_type': exception.__class__.__name__,
            'traceback': traceback.format_exc(),
            'extra_data': {
                'request_data': {
                    'GET': dict(request.GET),
                    'POST': self._safe_request_data(request.POST),
                }
            }
        }
        
        # Add to async queue
        log_collector.add_log('system', log_data)
    
    def _safe_request_data(self, data):
        """Sanitize request data (remove passwords, etc.)"""
        if not data:
            return {}
        
        sanitized = {}
        sensitive_keys = ['password', 'token', 'secret', 'key', 'api_key']
        
        for key, value in data.items():
            if any(sensitive in key.lower() for sensitive in sensitive_keys):
                sanitized[key] = '***REDACTED***'
            else:
                sanitized[key] = value
        
        return sanitized


class ActivityLoggingMiddleware:
    """
    Middleware for user activity logging
    Tracks user actions and page views
    """
    
    # Actions to track
    TRACKED_ACTIONS = {
        'POST': 'create',
        'PUT': 'update',
        'PATCH': 'update',
        'DELETE': 'delete',
        'GET': 'view'
    }
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Skip if user not authenticated
        if not request.user.is_authenticated:
            return self.get_response(request)
        
        # Skip static and media files
        if self._should_skip(request):
            return self.get_response(request)
        
        start_time = time.time()
        response = self.get_response(request)
        duration_ms = int((time.time() - start_time) * 1000)
        
        # Log activity asynchronously
        self._log_activity(request, response, duration_ms)
        
        return response
    
    def _should_skip(self, request):
        """Check if should skip logging this request"""
        skip_paths = ['/static/', '/media/', '/api/health/']
        return any(request.path.startswith(path) for path in skip_paths)
    
    def _log_activity(self, request, response, duration_ms):
        """Log user activity"""
        # Determine action
        action = self.TRACKED_ACTIONS.get(request.method, 'unknown')
        
        # Get module from URL
        module = ''
        if request.resolver_match:
            module = request.resolver_match.app_name or ''
        
        # Prepare log data
        log_data = {
            'user': request.user,
            'action': f"{action}_{module}" if module else action,
            'module': module,
            'page_url': request.path,
            'ip_address': self._get_client_ip(request),
            'user_agent': request.META.get('HTTP_USER_AGENT', ''),
            'success': 200 <= response.status_code < 400,
            'duration_ms': duration_ms,
            'metadata': {
                'method': request.method,
                'status_code': response.status_code,
            }
        }
        
        # Add error message if failed
        if not log_data['success']:
            log_data['error_message'] = f"HTTP {response.status_code}"
        
        # Add to async queue
        log_collector.add_log('activity', log_data)
    
    def _get_client_ip(self, request):
        """Get real client IP"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return request.META.get('REMOTE_ADDR')