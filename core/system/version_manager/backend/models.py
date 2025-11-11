"""
Version Manager Models
Database models for tracking version archives and analysis results
"""

from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
import json

User = get_user_model()


class VersionArchive(models.Model):
    """Model to store version archive information"""
    
    version = models.CharField(max_length=20, unique=True, db_index=True)
    path = models.CharField(max_length=500)
    size_bytes = models.BigIntegerField(default=0)
    size_mb = models.FloatField(default=0.0)
    file_count = models.IntegerField(default=0)
    directory_count = models.IntegerField(default=0)
    
    # Statistical analysis fields
    z_score = models.FloatField(default=0.0, null=True, blank=True)
    is_anomaly = models.BooleanField(default=False)
    anomaly_reason = models.CharField(max_length=100, blank=True, null=True)
    
    # Status fields
    STATUS_CHOICES = [
        ('normal', 'normal'),
        ('large', 'large (50-200 mb)'),
        ('very_large', 'very large (200-500 mb)'),
        ('huge', 'huge (500+ mb)'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='normal')
    
    # Timestamps
    created_at = models.DateTimeField(default=timezone.now)
    last_scanned = models.DateTimeField(auto_now=True)
    
    # Git information
    git_commit = models.CharField(max_length=40, blank=True, null=True)
    git_branch = models.CharField(max_length=100, blank=True, null=True)
    git_tag = models.CharField(max_length=50, blank=True, null=True)
    
    class Meta:
        ordering = ['-version']
        verbose_name = 'Version Archive'
        verbose_name_plural = 'Version Archives'
        indexes = [
            models.Index(fields=['version']),
            models.Index(fields=['size_mb']),
            models.Index(fields=['status']),
            models.Index(fields=['is_anomaly']),
        ]
    
    def __str__(self):
        return f"v{self.version} ({self.size_mb:.2f} MB)"
    
    def update_status(self):
        """Update status based on size"""
        if self.size_mb >= 500:
            self.status = 'huge'
        elif self.size_mb >= 200:
            self.status = 'very_large'
        elif self.size_mb >= 50:
            self.status = 'large'
        else:
            self.status = 'normal'
        return self.status
    
    def get_color_class(self):
        """Get CSS color class based on status"""
        color_map = {
            'huge': 'text-danger',
            'very_large': 'text-warning',
            'large': 'text-info',
            'normal': 'text-success'
        }
        return color_map.get(self.status, 'text-muted')
    
    def get_status_icon(self):
        """Get icon based on status"""
        icon_map = {
            'huge': '⚠️',
            'very_large': '⚠️',
            'large': '⚠️',
            'normal': '✓'
        }
        return icon_map.get(self.status, '')


class ScanSession(models.Model):
    """Model to track scanning sessions"""
    
    started_at = models.DateTimeField(default=timezone.now)
    completed_at = models.DateTimeField(null=True, blank=True)
    started_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Scan results
    total_archives = models.IntegerField(default=0)
    total_size_bytes = models.BigIntegerField(default=0)
    total_size_gb = models.FloatField(default=0.0)
    average_size_mb = models.FloatField(default=0.0)
    anomaly_count = models.IntegerField(default=0)
    
    # Progress tracking
    progress_percent = models.IntegerField(default=0)
    current_archive = models.CharField(max_length=100, blank=True)
    status_message = models.CharField(max_length=200, blank=True)
    is_complete = models.BooleanField(default=False)
    
    # Error tracking
    has_errors = models.BooleanField(default=False)
    error_message = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-started_at']
        verbose_name = 'Scan Session'
        verbose_name_plural = 'Scan Sessions'
    
    def __str__(self):
        return f"Scan {self.started_at.strftime('%Y-%m-%d %H:%M')}"
    
    def duration_seconds(self):
        """Get scan duration in seconds"""
        if self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return (timezone.now() - self.started_at).total_seconds()
    
    def duration_formatted(self):
        """Get formatted duration string"""
        seconds = self.duration_seconds()
        minutes = int(seconds // 60)
        remaining_seconds = int(seconds % 60)
        if minutes > 0:
            return f"{minutes}m {remaining_seconds}s"
        return f"{remaining_seconds}s"


class GitStatus(models.Model):
    """Model to cache git status information"""
    
    checked_at = models.DateTimeField(default=timezone.now)
    branch = models.CharField(max_length=100)
    commit_hash = models.CharField(max_length=40)
    commit_message = models.TextField(blank=True)
    author = models.CharField(max_length=200, blank=True)
    
    # File status
    modified_files = models.JSONField(default=list)
    untracked_files = models.JSONField(default=list)
    staged_files = models.JSONField(default=list)
    
    has_changes = models.BooleanField(default=False)
    ahead_count = models.IntegerField(default=0)
    behind_count = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['-checked_at']
        verbose_name = 'Git Status'
        verbose_name_plural = 'Git Statuses'
    
    def __str__(self):
        return f"Git Status @ {self.checked_at.strftime('%Y-%m-%d %H:%M')}"
    
    def get_status_summary(self):
        """Get a summary of the git status"""
        if not self.has_changes:
            return "Working directory clean"
        
        parts = []
        if self.modified_files:
            parts.append(f"{len(self.modified_files)} modified")
        if self.untracked_files:
            parts.append(f"{len(self.untracked_files)} untracked")
        if self.staged_files:
            parts.append(f"{len(self.staged_files)} staged")
        
        return ", ".join(parts)
