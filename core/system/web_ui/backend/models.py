"""
UNIBOS Web UI Models
Database models for the terminal-style web interface
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class SessionLog(models.Model):
    """Track web UI sessions"""
    
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    session_id = models.CharField(max_length=100, unique=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'web_ui_session_logs'
        ordering = ['-started_at']
        indexes = [
            models.Index(fields=['session_id']),
            models.Index(fields=['user', 'is_active']),
        ]
    
    def __str__(self):
        return f"Session {self.session_id} ({self.user or 'Anonymous'})"
    
    def end_session(self):
        """End the session"""
        self.is_active = False
        self.ended_at = timezone.now()
        self.save()


class ModuleAccess(models.Model):
    """Track module access and usage"""
    
    MODULE_CHOICES = [
        ('recaria', 'Recaria'),
        ('birlikteyiz', 'Birlikteyiz'),
        ('kisisel_enflasyon', 'Kişisel Enflasyon'),
        ('currencies', 'Currencies'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    module = models.CharField(max_length=50, choices=MODULE_CHOICES)
    accessed_at = models.DateTimeField(auto_now_add=True)
    session = models.ForeignKey(SessionLog, on_delete=models.CASCADE, null=True)
    action = models.CharField(max_length=100, null=True, blank=True)
    data = models.JSONField(null=True, blank=True)
    
    class Meta:
        db_table = 'web_ui_module_access'
        ordering = ['-accessed_at']
        indexes = [
            models.Index(fields=['user', 'module']),
            models.Index(fields=['module', 'accessed_at']),
        ]
    
    def __str__(self):
        return f"{self.user} accessed {self.module} at {self.accessed_at}"


class UIPreferences(models.Model):
    """User preferences for the web UI"""
    
    THEME_CHOICES = [
        ('dark', 'Dark Terminal'),
        ('light', 'Light Terminal'),
        ('retro', 'Retro Green'),
        ('amber', 'Amber CRT'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='ui_preferences')
    theme = models.CharField(max_length=20, choices=THEME_CHOICES, default='dark')
    font_size = models.IntegerField(default=14, help_text="Font size in pixels")
    show_animations = models.BooleanField(default=True)
    enable_sound = models.BooleanField(default=False)
    keyboard_shortcuts = models.BooleanField(default=True)
    auto_refresh = models.BooleanField(default=True)
    refresh_interval = models.IntegerField(default=5, help_text="Refresh interval in seconds")
    sidebar_collapsed = models.BooleanField(default=False)
    language = models.CharField(max_length=10, default='en')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'web_ui_preferences'
        verbose_name = 'UI Preference'
        verbose_name_plural = 'UI Preferences'
    
    def __str__(self):
        return f"UI Preferences for {self.user}"


class SystemStatus(models.Model):
    """System status tracking"""
    
    STATUS_CHOICES = [
        ('online', 'Online'),
        ('offline', 'Offline'),
        ('maintenance', 'Maintenance'),
        ('degraded', 'Degraded'),
    ]
    
    module = models.CharField(max_length=50)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    health_score = models.IntegerField(default=100, help_text="Health score 0-100")
    last_checked = models.DateTimeField(auto_now=True)
    error_count = models.IntegerField(default=0)
    warning_count = models.IntegerField(default=0)
    metadata = models.JSONField(null=True, blank=True)
    
    class Meta:
        db_table = 'web_ui_system_status'
        ordering = ['module']
        indexes = [
            models.Index(fields=['module', 'status']),
            models.Index(fields=['last_checked']),
        ]
    
    def __str__(self):
        return f"{self.module}: {self.status} ({self.health_score}%)"
    
    @classmethod
    def get_overall_status(cls):
        """Get overall system status"""
        statuses = cls.objects.all()
        if not statuses.exists():
            return 'unknown'
        
        if statuses.filter(status='offline').exists():
            return 'offline'
        elif statuses.filter(status='degraded').exists():
            return 'degraded'
        elif statuses.filter(status='maintenance').exists():
            return 'maintenance'
        
        return 'online'


class CommandHistory(models.Model):
    """Track command history for terminal-like experience"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    command = models.TextField()
    module = models.CharField(max_length=50, null=True, blank=True)
    executed_at = models.DateTimeField(auto_now_add=True)
    success = models.BooleanField(default=True)
    output = models.TextField(null=True, blank=True)
    error_message = models.TextField(null=True, blank=True)
    execution_time = models.FloatField(null=True, blank=True, help_text="Execution time in seconds")
    
    class Meta:
        db_table = 'web_ui_command_history'
        ordering = ['-executed_at']
        indexes = [
            models.Index(fields=['user', 'executed_at']),
            models.Index(fields=['module', 'executed_at']),
        ]
    
    def __str__(self):
        return f"{self.user}: {self.command[:50]}..."