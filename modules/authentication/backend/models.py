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