"""
Version Manager Admin Configuration
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import VersionArchive, ScanSession, GitStatus


@admin.register(VersionArchive)
class VersionArchiveAdmin(admin.ModelAdmin):
    """Admin interface for Version Archives"""
    
    list_display = [
        'version_display', 'size_display', 'file_count', 
        'status_badge', 'anomaly_badge', 'z_score', 'last_scanned'
    ]
    list_filter = ['status', 'is_anomaly', 'last_scanned']
    search_fields = ['version', 'path']
    readonly_fields = [
        'version', 'path', 'size_bytes', 'size_mb', 
        'file_count', 'directory_count', 'z_score', 
        'is_anomaly', 'anomaly_reason', 'status',
        'git_commit', 'git_branch', 'git_tag',
        'created_at', 'last_scanned'
    ]
    ordering = ['-version']
    
    def version_display(self, obj):
        """Display version with formatting"""
        return format_html('<strong>v{}</strong>', obj.version)
    version_display.short_description = 'Version'
    
    def size_display(self, obj):
        """Display size with color coding"""
        if obj.size_mb >= 500:
            color = '#ff4444'
        elif obj.size_mb >= 200:
            color = '#ff8c00'
        elif obj.size_mb >= 50:
            color = '#ffff00'
        else:
            color = '#00ff00'
        
        return format_html(
            '<span style="color: {};">{:.2f} MB</span>',
            color, obj.size_mb
        )
    size_display.short_description = 'Size'
    
    def status_badge(self, obj):
        """Display status as a badge"""
        colors = {
            'normal': '#28a745',
            'large': '#ffc107',
            'very_large': '#fd7e14',
            'huge': '#dc3545',
        }
        return format_html(
            '<span style="background: {}; color: white; padding: 3px 8px; '
            'border-radius: 3px; font-weight: bold;">{}</span>',
            colors.get(obj.status, '#6c757d'),
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def anomaly_badge(self, obj):
        """Display anomaly indicator"""
        if obj.is_anomaly:
            return format_html(
                '<span style="color: #dc3545; font-weight: bold;">⚠️ ANOMALY</span>'
            )
        return '-'
    anomaly_badge.short_description = 'Anomaly'


@admin.register(ScanSession)
class ScanSessionAdmin(admin.ModelAdmin):
    """Admin interface for Scan Sessions"""
    
    list_display = [
        'started_at', 'duration_formatted', 'progress_display',
        'total_archives', 'total_size_display', 'status_display'
    ]
    list_filter = ['is_complete', 'has_errors', 'started_at']
    readonly_fields = [
        'started_at', 'completed_at', 'started_by',
        'total_archives', 'total_size_bytes', 'total_size_gb',
        'average_size_mb', 'anomaly_count', 'progress_percent',
        'current_archive', 'status_message', 'is_complete',
        'has_errors', 'error_message'
    ]
    ordering = ['-started_at']
    
    def progress_display(self, obj):
        """Display progress bar"""
        color = '#28a745' if obj.is_complete else '#17a2b8'
        return format_html(
            '<div style="width: 100px; background: #e9ecef; '
            'border-radius: 3px; overflow: hidden;">'
            '<div style="width: {}%; background: {}; height: 20px;"></div>'
            '</div>',
            obj.progress_percent, color
        )
    progress_display.short_description = 'Progress'
    
    def total_size_display(self, obj):
        """Display total size in GB"""
        return format_html('{:.2f} GB', obj.total_size_gb)
    total_size_display.short_description = 'Total Size'
    
    def status_display(self, obj):
        """Display scan status"""
        if obj.has_errors:
            return format_html(
                '<span style="color: #dc3545;">❌ Failed</span>'
            )
        elif obj.is_complete:
            return format_html(
                '<span style="color: #28a745;">✓ Complete</span>'
            )
        else:
            return format_html(
                '<span style="color: #17a2b8;">⏳ Running</span>'
            )
    status_display.short_description = 'Status'


@admin.register(GitStatus)
class GitStatusAdmin(admin.ModelAdmin):
    """Admin interface for Git Status"""
    
    list_display = [
        'checked_at', 'branch', 'commit_short', 
        'changes_summary', 'has_changes'
    ]
    list_filter = ['has_changes', 'branch', 'checked_at']
    readonly_fields = [
        'checked_at', 'branch', 'commit_hash', 'commit_message',
        'author', 'modified_files', 'untracked_files', 'staged_files',
        'has_changes', 'ahead_count', 'behind_count'
    ]
    ordering = ['-checked_at']
    
    def commit_short(self, obj):
        """Display short commit hash"""
        return obj.commit_hash[:8] if obj.commit_hash else '-'
    commit_short.short_description = 'Commit'
    
    def changes_summary(self, obj):
        """Display changes summary"""
        return obj.get_status_summary()
    changes_summary.short_description = 'Changes'
