"""
User models for UNIBOS
Extends Django's AbstractUser with additional fields
"""

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.core.validators import RegexValidator
import uuid


class User(AbstractUser):
    """Custom user model with extended fields"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Additional profile fields
    email = models.EmailField(unique=True, db_index=True)
    phone_number = models.CharField(
        max_length=20,
        blank=True,
        validators=[
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$',
                message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
            )
        ]
    )
    
    # Profile information
    bio = models.TextField(blank=True, max_length=500)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    
    # Location
    country = models.CharField(max_length=2, blank=True)  # ISO 3166-1 alpha-2
    city = models.CharField(max_length=100, blank=True)
    user_timezone = models.CharField(max_length=50, default='Europe/Istanbul')
    
    # Preferences
    language = models.CharField(max_length=10, default='tr')
    theme = models.CharField(max_length=20, default='light')
    notifications_enabled = models.BooleanField(default=True)
    email_notifications = models.BooleanField(default=True)
    
    # Security
    is_verified = models.BooleanField(default=False)
    verification_token = models.CharField(max_length=100, blank=True)
    last_password_change = models.DateTimeField(default=timezone.now)
    require_password_change = models.BooleanField(default=False)
    
    # Activity tracking
    last_activity = models.DateTimeField(blank=True, null=True)
    login_count = models.PositiveIntegerField(default=0)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Relations
    blocked_users = models.ManyToManyField(
        'self',
        symmetrical=False,
        related_name='blocked_by',
        blank=True
    )
    
    class Meta:
        db_table = 'users'
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['username']),
            models.Index(fields=['is_active', 'is_verified']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return self.username
    
    @property
    def full_name(self):
        """Get user's full name"""
        return f"{self.first_name} {self.last_name}".strip() or self.username
    
    def update_last_activity(self):
        """Update last activity timestamp"""
        self.last_activity = timezone.now()
        self.save(update_fields=['last_activity'])
    
    def increment_login_count(self):
        """Increment login counter"""
        self.login_count += 1
        self.save(update_fields=['login_count'])


class UserProfile(models.Model):
    """Extended user profile for additional data"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    # Professional information
    occupation = models.CharField(max_length=100, blank=True)
    company = models.CharField(max_length=100, blank=True)
    website = models.URLField(blank=True)
    linkedin = models.URLField(blank=True)
    github = models.CharField(max_length=50, blank=True)
    
    # App-specific settings
    default_currency = models.CharField(max_length=3, default='TRY')
    inflation_basket = models.JSONField(default=dict)  # Personal inflation tracking
    recaria_stats = models.JSONField(default=dict)  # Game statistics
    birlikteyiz_id = models.CharField(max_length=50, blank=True)  # Mesh network ID
    
    # Privacy settings
    profile_visibility = models.CharField(
        max_length=20,
        choices=[
            ('public', 'Public'),
            ('friends', 'Friends Only'),
            ('private', 'Private'),
        ],
        default='friends'
    )
    show_online_status = models.BooleanField(default=True)
    
    # Statistics
    total_points = models.PositiveIntegerField(default=0)
    level = models.PositiveIntegerField(default=1)
    achievements = models.JSONField(default=list)
    
    class Meta:
        db_table = 'user_profiles'
    
    def __str__(self):
        return f"Profile for {self.user.username}"


class UserDevice(models.Model):
    """Track user devices for security and push notifications"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='devices')
    
    # Device identification
    device_id = models.CharField(max_length=255, unique=True)
    device_type = models.CharField(
        max_length=20,
        choices=[
            ('web', 'Web Browser'),
            ('ios', 'iOS'),
            ('android', 'Android'),
            ('desktop', 'Desktop App'),
        ]
    )
    device_name = models.CharField(max_length=100)
    device_model = models.CharField(max_length=100, blank=True)
    
    # Push notification token
    push_token = models.TextField(blank=True)
    
    # Metadata
    last_used = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'user_devices'
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['device_id']),
        ]
        ordering = ['-last_used']
    
    def __str__(self):
        return f"{self.device_name} ({self.device_type}) for {self.user.username}"


class UserNotification(models.Model):
    """User notifications"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    
    # Notification content
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(
        max_length=50,
        choices=[
            ('info', 'Information'),
            ('success', 'Success'),
            ('warning', 'Warning'),
            ('error', 'Error'),
            ('currency_alert', 'Currency Alert'),
            ('inflation_update', 'Inflation Update'),
            ('game_event', 'Game Event'),
            ('emergency', 'Emergency'),
        ]
    )
    
    # Related object (generic relation)
    related_object_type = models.CharField(max_length=50, blank=True)
    related_object_id = models.CharField(max_length=50, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)
    is_read = models.BooleanField(default=False)
    
    # Action URL
    action_url = models.CharField(max_length=200, blank=True)
    
    class Meta:
        db_table = 'user_notifications'
        indexes = [
            models.Index(fields=['user', 'is_read']),
            models.Index(fields=['created_at']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.notification_type}: {self.title}"
    
    def mark_read(self):
        """Mark notification as read"""
        self.is_read = True
        self.read_at = timezone.now()
        self.save(update_fields=['is_read', 'read_at'])