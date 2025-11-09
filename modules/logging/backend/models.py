"""
System and Activity logging models for UNIBOS
Optimized for high-volume logging with minimal performance impact
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import ArrayField
from django.contrib.postgres.indexes import BrinIndex, GinIndex
from django.utils import timezone
from django.core.cache import cache
import json
import uuid

User = get_user_model()


class LogLevel(models.TextChoices):
    """Log severity levels"""
    DEBUG = 'debug', 'debug'
    INFO = 'info', 'info'
    WARNING = 'warning', 'warning'
    ERROR = 'error', 'error'
    CRITICAL = 'critical', 'critical'


class LogCategory(models.TextChoices):
    """Log categories for filtering"""
    AUTH = 'auth', 'authentication'
    API = 'api', 'api calls'
    ADMIN = 'admin', 'administration'
    USER = 'user', 'user actions'
    SYSTEM = 'system', 'system events'
    SECURITY = 'security', 'security events'
    PAYMENT = 'payment', 'payment events'
    MODULE = 'module', 'module actions'
    DATABASE = 'database', 'database operations'
    PERFORMANCE = 'performance', 'performance metrics'


class SystemLog(models.Model):
    """
    High-performance system log model
    Uses BRIN indexes for time-series data
    """
    id = models.BigAutoField(primary_key=True)  # BigInt for high volume
    timestamp = models.DateTimeField(default=timezone.now, db_index=False)  # BRIN index instead
    
    # Log information
    level = models.CharField(max_length=10, choices=LogLevel.choices, default=LogLevel.INFO)
    category = models.CharField(max_length=20, choices=LogCategory.choices)
    message = models.TextField()
    
    # Context
    module = models.CharField(max_length=100, blank=True)  # Which module/app
    function = models.CharField(max_length=100, blank=True)  # Function name
    
    # Request information (optional)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    request_method = models.CharField(max_length=10, blank=True)
    request_path = models.CharField(max_length=500, blank=True)
    
    # User (optional - null for system events)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    session_key = models.CharField(max_length=100, blank=True)
    
    # Additional data (JSON)
    extra_data = models.JSONField(default=dict, blank=True)
    
    # Error information (for errors/exceptions)
    exception_type = models.CharField(max_length=100, blank=True)
    traceback = models.TextField(blank=True)
    
    # Performance metrics (optional)
    duration_ms = models.IntegerField(null=True, blank=True)  # Request duration in ms
    
    class Meta:
        db_table = 'system_logs'
        indexes = [
            BrinIndex(fields=['timestamp']),  # BRIN for time-series
            models.Index(fields=['level', 'category']),
            models.Index(fields=['user', 'timestamp']),
            GinIndex(fields=['extra_data']),  # GIN for JSON queries
        ]
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"[{self.level}] {self.category}: {self.message[:50]}"


class ActivityLog(models.Model):
    """
    User activity log for tracking user actions
    Separate from system logs for better performance
    """
    id = models.BigAutoField(primary_key=True)
    timestamp = models.DateTimeField(default=timezone.now, db_index=False)  # BRIN index
    
    # User information
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activity_logs')
    
    # Action information
    action = models.CharField(max_length=100)  # e.g., 'login', 'view_page', 'create_item'
    object_type = models.CharField(max_length=50, blank=True)  # e.g., 'document', 'user'
    object_id = models.CharField(max_length=100, blank=True)  # ID of affected object
    object_repr = models.CharField(max_length=200, blank=True)  # String representation
    
    # Module/Page
    module = models.CharField(max_length=50, blank=True)
    page_url = models.CharField(max_length=500, blank=True)
    
    # Request context
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    
    # Result
    success = models.BooleanField(default=True)
    error_message = models.TextField(blank=True)
    
    # Additional context
    metadata = models.JSONField(default=dict, blank=True)
    
    # Performance
    duration_ms = models.IntegerField(null=True, blank=True)
    
    class Meta:
        db_table = 'activity_logs'
        indexes = [
            BrinIndex(fields=['timestamp']),
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['action', 'timestamp']),
            models.Index(fields=['module', 'timestamp']),
            GinIndex(fields=['metadata']),
        ]
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.user.username} - {self.action} at {self.timestamp}"


class LogAggregation(models.Model):
    """
    Pre-aggregated log statistics for dashboard
    Updated hourly via cron job
    """
    date_hour = models.DateTimeField(unique=True)
    
    # Counts by level
    debug_count = models.IntegerField(default=0)
    info_count = models.IntegerField(default=0)
    warning_count = models.IntegerField(default=0)
    error_count = models.IntegerField(default=0)
    critical_count = models.IntegerField(default=0)
    
    # Counts by category
    category_counts = models.JSONField(default=dict)
    
    # User activity
    active_users = models.IntegerField(default=0)
    total_actions = models.IntegerField(default=0)
    
    # Performance
    avg_response_time = models.FloatField(null=True, blank=True)
    p95_response_time = models.FloatField(null=True, blank=True)
    p99_response_time = models.FloatField(null=True, blank=True)
    
    # Top errors
    top_errors = models.JSONField(default=list)  # List of most common errors
    
    class Meta:
        db_table = 'log_aggregations'
        indexes = [
            models.Index(fields=['-date_hour']),
        ]
        ordering = ['-date_hour']


class LogRetentionPolicy(models.Model):
    """
    Configurable retention policies for different log types
    """
    log_type = models.CharField(max_length=50, unique=True)
    retention_days = models.IntegerField(default=30)
    is_active = models.BooleanField(default=True)
    
    # Archive settings
    archive_enabled = models.BooleanField(default=False)
    archive_path = models.CharField(max_length=500, blank=True)
    
    class Meta:
        db_table = 'log_retention_policies'
        verbose_name_plural = 'Log retention policies'
    
    def __str__(self):
        return f"{self.log_type}: {self.retention_days} days"


# Log buffer for batch inserts
class LogBuffer:
    """
    In-memory buffer for batch log inserts
    Flushes to database every N logs or T seconds
    """
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.system_logs = []
            cls._instance.activity_logs = []
            cls._instance.last_flush = timezone.now()
        return cls._instance
    
    def add_system_log(self, **kwargs):
        """Add a system log to buffer"""
        self.system_logs.append(SystemLog(**kwargs))
        self._check_flush()
    
    def add_activity_log(self, **kwargs):
        """Add an activity log to buffer"""
        self.activity_logs.append(ActivityLog(**kwargs))
        self._check_flush()
    
    def _check_flush(self):
        """Check if buffer should be flushed"""
        # Flush if more than 100 logs or 5 seconds passed
        if (len(self.system_logs) + len(self.activity_logs) >= 100 or
            (timezone.now() - self.last_flush).seconds >= 5):
            self.flush()
    
    def flush(self):
        """Flush logs to database"""
        if self.system_logs:
            SystemLog.objects.bulk_create(self.system_logs, ignore_conflicts=True)
            self.system_logs.clear()
        
        if self.activity_logs:
            ActivityLog.objects.bulk_create(self.activity_logs, ignore_conflicts=True)
            self.activity_logs.clear()
        
        self.last_flush = timezone.now()


# Global log buffer instance
log_buffer = LogBuffer()