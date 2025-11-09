"""
OMDB API Integration Models
Manages API keys, usage tracking, and caching
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.exceptions import ValidationError
from cryptography.fernet import Fernet
from django.conf import settings
import uuid
from datetime import datetime, timedelta
import json

User = get_user_model()


class APIKeyManager(models.Model):
    """Secure storage and management of OMDB API keys"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Encrypted API key storage
    encrypted_key = models.TextField()
    key_name = models.CharField(max_length=100, default="OMDB API")
    
    # Usage limits
    daily_limit = models.IntegerField(default=1000)
    requests_today = models.IntegerField(default=0)
    last_reset_date = models.DateField(default=timezone.now)
    
    # Status
    is_active = models.BooleanField(default=True)
    is_patron = models.BooleanField(default=False, help_text="Patron status for poster API")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "API Key"
        verbose_name_plural = "API Keys"
    
    def save(self, *args, **kwargs):
        # Ensure only one active key at a time
        if self.is_active:
            APIKeyManager.objects.exclude(pk=self.pk).update(is_active=False)
        super().save(*args, **kwargs)
    
    def set_api_key(self, api_key):
        """Encrypt and store API key"""
        # Generate encryption key if not exists
        if not hasattr(settings, 'MOVIES_ENCRYPTION_KEY'):
            settings.MOVIES_ENCRYPTION_KEY = Fernet.generate_key()
        
        cipher = Fernet(settings.MOVIES_ENCRYPTION_KEY)
        self.encrypted_key = cipher.encrypt(api_key.encode()).decode()
    
    def get_api_key(self):
        """Decrypt and return API key"""
        # Load encryption key from file if not in settings
        if not hasattr(settings, 'MOVIES_ENCRYPTION_KEY'):
            import os
            encryption_key_path = os.path.join(settings.BASE_DIR, '.movies_encryption_key')
            if os.path.exists(encryption_key_path):
                with open(encryption_key_path, 'rb') as f:
                    settings.MOVIES_ENCRYPTION_KEY = f.read()
            else:
                raise ValidationError("Encryption key not found")
        
        cipher = Fernet(settings.MOVIES_ENCRYPTION_KEY)
        return cipher.decrypt(self.encrypted_key.encode()).decode()
    
    def check_and_reset_daily_limit(self):
        """Reset daily counter if new day"""
        today = timezone.now().date()
        # Convert to date if it's datetime
        last_reset = self.last_reset_date
        if hasattr(last_reset, 'date'):
            last_reset = last_reset.date()
        if last_reset < today:
            self.requests_today = 0
            self.last_reset_date = today
            self.save()
    
    def can_make_request(self):
        """Check if we can make another API request"""
        self.check_and_reset_daily_limit()
        return self.requests_today < self.daily_limit
    
    def increment_usage(self):
        """Increment usage counter"""
        self.check_and_reset_daily_limit()
        if self.can_make_request():
            self.requests_today += 1
            self.save()
            return True
        return False
    
    @property
    def remaining_requests(self):
        """Get remaining requests for today"""
        self.check_and_reset_daily_limit()
        return self.daily_limit - self.requests_today
    
    def __str__(self):
        return f"{self.key_name} - {self.remaining_requests}/{self.daily_limit} remaining"


class OMDBCache(models.Model):
    """Cache OMDB API responses to minimize API calls"""
    
    CACHE_TYPE_CHOICES = [
        ('search', 'Search Results'),
        ('detail', 'Movie Details'),
        ('poster', 'Poster Data'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Cache key and type
    cache_key = models.CharField(max_length=255, unique=True, db_index=True)
    cache_type = models.CharField(max_length=20, choices=CACHE_TYPE_CHOICES)
    
    # Query parameters
    query_params = models.JSONField()
    
    # Response data
    response_data = models.JSONField()
    response_status = models.IntegerField(default=200)
    
    # Metadata
    hit_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField()
    
    class Meta:
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['cache_type', '-updated_at']),
            models.Index(fields=['expires_at']),
        ]
    
    @classmethod
    def get_cache(cls, cache_key, cache_type='search'):
        """Get cached response if valid"""
        try:
            cache = cls.objects.get(
                cache_key=cache_key,
                cache_type=cache_type,
                expires_at__gt=timezone.now()
            )
            cache.hit_count += 1
            cache.save()
            return cache.response_data
        except cls.DoesNotExist:
            return None
    
    @classmethod
    def set_cache(cls, cache_key, query_params, response_data, cache_type='search', hours=24):
        """Set or update cache entry"""
        expires_at = timezone.now() + timedelta(hours=hours)
        
        cache, created = cls.objects.update_or_create(
            cache_key=cache_key,
            cache_type=cache_type,
            defaults={
                'query_params': query_params,
                'response_data': response_data,
                'expires_at': expires_at,
            }
        )
        return cache
    
    @classmethod
    def clear_expired(cls):
        """Remove expired cache entries"""
        return cls.objects.filter(expires_at__lt=timezone.now()).delete()
    
    def __str__(self):
        return f"{self.cache_type}: {self.cache_key} (hits: {self.hit_count})"


class APIUsageLog(models.Model):
    """Log all API requests for analytics and debugging"""
    
    REQUEST_TYPE_CHOICES = [
        ('search', 'Search'),
        ('detail', 'Movie Details'),
        ('poster', 'Poster'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Request info
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='omdb_requests')
    request_type = models.CharField(max_length=20, choices=REQUEST_TYPE_CHOICES)
    query_params = models.JSONField()
    
    # Response info
    response_status = models.IntegerField()
    response_time_ms = models.IntegerField()
    from_cache = models.BooleanField(default=False)
    
    # Error tracking
    error_message = models.TextField(blank=True)
    
    # Timestamps
    requested_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-requested_at']
        indexes = [
            models.Index(fields=['user', '-requested_at']),
            models.Index(fields=['request_type', '-requested_at']),
            models.Index(fields=['from_cache', '-requested_at']),
        ]
    
    @classmethod
    def log_request(cls, user, request_type, query_params, response_status, 
                    response_time_ms, from_cache=False, error_message=''):
        """Create a usage log entry"""
        return cls.objects.create(
            user=user,
            request_type=request_type,
            query_params=query_params,
            response_status=response_status,
            response_time_ms=response_time_ms,
            from_cache=from_cache,
            error_message=error_message
        )
    
    def __str__(self):
        cache_str = " (cached)" if self.from_cache else ""
        return f"{self.user.username if self.user else 'Anonymous'} - {self.request_type}{cache_str} - {self.requested_at}"


class MovieImportQueue(models.Model):
    """Queue for batch importing movies from OMDB"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Import details
    imdb_id = models.CharField(max_length=20, unique=True)
    requested_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Processing info
    attempts = models.IntegerField(default=0)
    error_message = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['status', 'created_at']
        indexes = [
            models.Index(fields=['status', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.imdb_id} - {self.status}"