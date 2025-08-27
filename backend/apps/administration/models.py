from django.db import models
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from django.contrib.auth.hashers import make_password, check_password
from apps.core.models import BaseModel
import json


class Role(BaseModel):
    """Custom role model for advanced permission management"""
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    permissions = models.ManyToManyField(Permission, blank=True)
    groups = models.ManyToManyField(Group, blank=True, related_name='custom_roles')
    is_system = models.BooleanField(default=False)  # System roles can't be deleted
    priority = models.IntegerField(default=0)  # Higher priority = more important
    
    # Role settings
    can_manage_users = models.BooleanField(default=False)
    can_manage_roles = models.BooleanField(default=False)
    can_view_logs = models.BooleanField(default=False)
    can_access_admin = models.BooleanField(default=False)
    can_export_data = models.BooleanField(default=False)
    can_import_data = models.BooleanField(default=False)
    
    # Module-specific permissions
    module_permissions = models.JSONField(default=dict, blank=True)
    
    class Meta:
        ordering = ['-priority', 'name']
    
    def __str__(self):
        return self.name
    
    def get_all_permissions(self):
        """Get all permissions including inherited from groups"""
        perms = set(self.permissions.all())
        for group in self.groups.all():
            perms.update(group.permissions.all())
        return perms


class UserRole(BaseModel):
    """Many-to-many relationship between users and roles with additional metadata"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='user_roles')
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='user_assignments')
    assigned_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='role_assignments_made')
    assigned_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    is_temporary = models.BooleanField(default=False)
    notes = models.TextField(blank=True)
    
    class Meta:
        unique_together = ['user', 'role']
        ordering = ['-assigned_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.role.name}"
    
    @property
    def is_expired(self):
        if self.expires_at:
            from django.utils import timezone
            return timezone.now() > self.expires_at
        return False


class Department(BaseModel):
    """Department/Team structure for organizing users"""
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subdepartments')
    manager = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='managed_departments')
    members = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='departments')
    default_role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def get_hierarchy_name(self):
        """Get full hierarchy name like 'IT > Development > Frontend'"""
        names = [self.name]
        parent = self.parent
        while parent:
            names.insert(0, parent.name)
            parent = parent.parent
        return ' > '.join(names)


class PermissionRequest(BaseModel):
    """Track permission/role requests"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('expired', 'Expired'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='permission_requests')
    role = models.ForeignKey(Role, on_delete=models.CASCADE, null=True, blank=True)
    permissions = models.ManyToManyField(Permission, blank=True)
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    requested_at = models.DateTimeField(auto_now_add=True)
    reviewed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='permission_reviews')
    reviewed_at = models.DateTimeField(null=True, blank=True)
    review_notes = models.TextField(blank=True)
    duration_days = models.IntegerField(null=True, blank=True)  # Temporary permission duration
    
    class Meta:
        ordering = ['-requested_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.role.name if self.role else 'Custom'} - {self.status}"


class AuditLog(BaseModel):
    """Track all administrative actions"""
    ACTION_TYPES = [
        ('login', 'User Login'),
        ('logout', 'User Logout'),
        ('role_assign', 'Role Assigned'),
        ('role_remove', 'Role Removed'),
        ('permission_grant', 'Permission Granted'),
        ('permission_revoke', 'Permission Revoked'),
        ('user_create', 'User Created'),
        ('user_update', 'User Updated'),
        ('user_delete', 'User Deleted'),
        ('group_change', 'Group Changed'),
        ('password_change', 'Password Changed'),
        ('failed_login', 'Failed Login'),
        ('data_export', 'Data Exported'),
        ('data_import', 'Data Imported'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='audit_logs')
    action = models.CharField(max_length=50, choices=ACTION_TYPES)
    target_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='audit_logs_as_target')
    target_object = models.CharField(max_length=200, blank=True)
    details = models.JSONField(default=dict, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['-timestamp']),
            models.Index(fields=['user', '-timestamp']),
            models.Index(fields=['action', '-timestamp']),
        ]
    
    def __str__(self):
        return f"{self.user.username if self.user else 'System'} - {self.get_action_display()} - {self.timestamp}"


class ScreenLock(BaseModel):
    """Screen lock settings for users"""
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='screen_lock')
    is_enabled = models.BooleanField(default=False)
    password_hash = models.CharField(max_length=255, blank=True)
    lock_timeout = models.IntegerField(default=300)  # seconds (5 minutes default)
    auto_lock = models.BooleanField(default=True)
    require_on_startup = models.BooleanField(default=False)
    failed_attempts = models.IntegerField(default=0)
    locked_until = models.DateTimeField(null=True, blank=True)
    last_locked = models.DateTimeField(null=True, blank=True)
    last_unlocked = models.DateTimeField(null=True, blank=True)
    
    # Security settings
    max_failed_attempts = models.IntegerField(default=5)
    lockout_duration = models.IntegerField(default=300)  # seconds (5 minutes)
    require_password_change = models.BooleanField(default=False)
    
    def set_password(self, password):
        """Set the screen lock password"""
        self.password_hash = make_password(password)
        self.failed_attempts = 0
        self.locked_until = None
        self.save()
    
    def check_password(self, password):
        """Check if the provided password is correct"""
        if not self.password_hash:
            return False
        return check_password(password, self.password_hash)
    
    def is_locked_out(self):
        """Check if the user is currently locked out"""
        from django.utils import timezone
        if self.locked_until and self.locked_until > timezone.now():
            return True
        return False
    
    def record_failed_attempt(self):
        """Record a failed unlock attempt"""
        from django.utils import timezone
        self.failed_attempts += 1
        if self.failed_attempts >= self.max_failed_attempts:
            from datetime import timedelta
            self.locked_until = timezone.now() + timedelta(seconds=self.lockout_duration)
        self.save()
    
    def reset_failed_attempts(self):
        """Reset failed attempts after successful unlock"""
        self.failed_attempts = 0
        self.locked_until = None
        self.save()
    
    def __str__(self):
        return f"Screen Lock for {self.user.username}"
    
    class Meta:
        verbose_name = "Screen Lock"
        verbose_name_plural = "Screen Locks"


class RecariaMailbox(BaseModel):
    """recaria.org mailbox management"""
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='recaria_mailbox')
    email_address = models.EmailField(unique=True)
    mailbox_created = models.BooleanField(default=False)
    mailbox_size_mb = models.IntegerField(default=1024)  # Default 1GB
    password_set = models.BooleanField(default=False)
    
    # Mail server settings
    imap_enabled = models.BooleanField(default=True)
    pop3_enabled = models.BooleanField(default=False)
    smtp_enabled = models.BooleanField(default=True)
    
    # Quotas and limits
    daily_send_limit = models.IntegerField(default=500)
    attachment_size_limit_mb = models.IntegerField(default=25)
    
    # Auto-responder
    auto_responder_enabled = models.BooleanField(default=False)
    auto_responder_message = models.TextField(blank=True)
    
    # Forwarding
    forwarding_enabled = models.BooleanField(default=False)
    forwarding_address = models.EmailField(blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    suspended_reason = models.TextField(blank=True)
    
    # Statistics
    messages_sent = models.IntegerField(default=0)
    messages_received = models.IntegerField(default=0)
    current_usage_mb = models.FloatField(default=0)
    last_login = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['email_address']
        verbose_name = 'recaria.org mailbox'
        verbose_name_plural = 'recaria.org mailboxes'
        
    def __str__(self):
        return self.email_address
    
    @property
    def usage_percentage(self):
        """calculate mailbox usage percentage"""
        if self.mailbox_size_mb == 0:
            return 0
        return min(100, (self.current_usage_mb / self.mailbox_size_mb) * 100)
    
    @property
    def is_over_quota(self):
        """check if mailbox is over quota"""
        return self.current_usage_mb >= self.mailbox_size_mb


class SystemSetting(BaseModel):
    """System-wide settings for administration"""
    key = models.CharField(max_length=100, unique=True)
    value = models.JSONField()
    description = models.TextField(blank=True)
    is_public = models.BooleanField(default=False)  # Can be viewed by all users
    
    class Meta:
        ordering = ['key']
    
    def __str__(self):
        return self.key
    
    @classmethod
    def get(cls, key, default=None):
        try:
            return cls.objects.get(key=key).value
        except cls.DoesNotExist:
            return default
    
    @classmethod
    def set(cls, key, value, description=''):
        obj, created = cls.objects.update_or_create(
            key=key,
            defaults={'value': value, 'description': description}
        )
        return obj