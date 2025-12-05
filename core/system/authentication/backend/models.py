"""
Authentication models for UNIBOS
Includes JWT token blacklisting and session management
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
import uuid

User = get_user_model()


class RefreshTokenBlacklist(models.Model):
    """Model to store blacklisted refresh tokens"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    token = models.CharField(max_length=500, unique=True, db_index=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blacklisted_tokens')
    blacklisted_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    
    class Meta:
        db_table = 'auth_refresh_token_blacklist'
        indexes = [
            models.Index(fields=['expires_at']),
            models.Index(fields=['user', 'blacklisted_at']),
        ]
        ordering = ['-blacklisted_at']
    
    def __str__(self):
        return f"Blacklisted token for {self.user.username}"
    
    @classmethod
    def cleanup_expired(cls):
        """Remove expired blacklisted tokens"""
        return cls.objects.filter(expires_at__lt=timezone.now()).delete()


class UserSession(models.Model):
    """Track active user sessions for security monitoring"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sessions')
    session_key = models.CharField(max_length=100, unique=True)
    
    # Session metadata
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    device_info = models.JSONField(default=dict)
    
    # Location info (optional)
    country = models.CharField(max_length=2, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField()
    
    # Security flags
    is_active = models.BooleanField(default=True)
    is_suspicious = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'auth_user_sessions'
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['expires_at']),
            models.Index(fields=['last_activity']),
        ]
        ordering = ['-last_activity']
    
    def __str__(self):
        return f"Session for {self.user.username} from {self.ip_address}"
    
    def is_expired(self):
        return timezone.now() > self.expires_at
    
    def refresh(self):
        """Refresh session expiration"""
        self.expires_at = timezone.now() + timedelta(days=7)
        self.save(update_fields=['expires_at', 'last_activity'])
    
    @classmethod
    def cleanup_expired(cls):
        """Remove expired sessions"""
        return cls.objects.filter(expires_at__lt=timezone.now()).delete()


class LoginAttempt(models.Model):
    """Track login attempts for security monitoring"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(max_length=150, db_index=True)
    ip_address = models.GenericIPAddressField(db_index=True)
    user_agent = models.TextField()
    
    # Attempt result
    is_successful = models.BooleanField(default=False)
    failure_reason = models.CharField(max_length=100, blank=True)
    
    # Timestamps
    attempted_at = models.DateTimeField(auto_now_add=True)
    
    # Related user (if successful)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='login_attempts')
    
    class Meta:
        db_table = 'auth_login_attempts'
        indexes = [
            models.Index(fields=['ip_address', 'attempted_at']),
            models.Index(fields=['username', 'attempted_at']),
            models.Index(fields=['attempted_at']),
        ]
        ordering = ['-attempted_at']
    
    def __str__(self):
        status = "successful" if self.is_successful else "failed"
        return f"{status} login attempt for {self.username} from {self.ip_address}"
    
    @classmethod
    def get_recent_failures(cls, ip_address=None, username=None, minutes=30):
        """Get recent failed login attempts"""
        since = timezone.now() - timedelta(minutes=minutes)
        queryset = cls.objects.filter(
            is_successful=False,
            attempted_at__gte=since
        )
        
        if ip_address:
            queryset = queryset.filter(ip_address=ip_address)
        if username:
            queryset = queryset.filter(username=username)
        
        return queryset.count()


class PasswordResetToken(models.Model):
    """Secure password reset tokens"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='password_reset_tokens')
    token = models.CharField(max_length=100, unique=True)
    
    # Security
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    used_at = models.DateTimeField(null=True, blank=True)
    
    # Status
    is_used = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'auth_password_reset_tokens'
        indexes = [
            models.Index(fields=['token', 'is_used']),
            models.Index(fields=['expires_at']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Password reset token for {self.user.username}"
    
    def is_valid(self):
        """Check if token is valid"""
        return not self.is_used and timezone.now() < self.expires_at
    
    def mark_used(self):
        """Mark token as used"""
        self.is_used = True
        self.used_at = timezone.now()
        self.save(update_fields=['is_used', 'used_at'])


class TwoFactorAuth(models.Model):
    """Two-factor authentication settings"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='two_factor')
    secret = models.CharField(max_length=32)
    is_enabled = models.BooleanField(default=False)

    # Backup codes
    backup_codes = models.JSONField(default=list)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    last_used_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'auth_two_factor'

    def __str__(self):
        status = "enabled" if self.is_enabled else "disabled"
        return f"2FA {status} for {self.user.username}"


class UserOfflineCache(models.Model):
    """
    Cache for Hub user credentials to enable offline authentication on Nodes.

    When a user logs in via Hub, nodes can cache their credentials here.
    This allows the user to authenticate on the node even when Hub is unreachable.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # User identification (from Hub)
    global_uuid = models.UUIDField(unique=True, db_index=True)
    username = models.CharField(max_length=150, db_index=True)
    email = models.EmailField(db_index=True)

    # User info
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    # Offline authentication
    offline_hash = models.CharField(max_length=128)  # bcrypt hash for offline verification

    # Cached permissions (from Hub)
    cached_permissions = models.JSONField(default=dict)
    cached_roles = models.JSONField(default=list)

    # Cache validity
    cached_at = models.DateTimeField(auto_now=True)
    cache_valid_until = models.DateTimeField()  # Default 7 days from cache time

    # Hub sync tracking
    last_synced_with_hub = models.DateTimeField(null=True, blank=True)
    hub_url = models.URLField(blank=True)  # Which hub this cache came from

    class Meta:
        db_table = 'auth_user_offline_cache'
        indexes = [
            models.Index(fields=['username']),
            models.Index(fields=['email']),
            models.Index(fields=['cache_valid_until']),
        ]
        ordering = ['-cached_at']

    def __str__(self):
        return f"Offline cache for {self.username} (valid until {self.cache_valid_until})"

    def is_valid(self):
        """Check if cache is still valid"""
        return timezone.now() < self.cache_valid_until

    def refresh_validity(self, days=7):
        """Extend cache validity"""
        self.cache_valid_until = timezone.now() + timedelta(days=days)
        self.save(update_fields=['cache_valid_until', 'cached_at'])

    @classmethod
    def cache_from_hub_response(cls, hub_response, offline_hash, hub_url=''):
        """
        Create or update cache from Hub login response

        Args:
            hub_response: Dict with user data from Hub login
            offline_hash: The user's password hash for offline verification
            hub_url: URL of the Hub that provided this data
        """
        user_data = hub_response.get('user', {})

        cache_entry, created = cls.objects.update_or_create(
            global_uuid=user_data.get('id'),
            defaults={
                'username': user_data.get('username', ''),
                'email': user_data.get('email', ''),
                'first_name': user_data.get('first_name', ''),
                'last_name': user_data.get('last_name', ''),
                'is_staff': user_data.get('is_staff', False),
                'is_superuser': user_data.get('is_superuser', False),
                'offline_hash': offline_hash,
                'cached_permissions': user_data.get('permissions', []),
                'cached_roles': user_data.get('roles', []),
                'cache_valid_until': timezone.now() + timedelta(days=7),
                'last_synced_with_hub': timezone.now(),
                'hub_url': hub_url,
            }
        )

        return cache_entry, created

    @classmethod
    def cleanup_expired(cls):
        """Remove expired cache entries"""
        return cls.objects.filter(cache_valid_until__lt=timezone.now()).delete()