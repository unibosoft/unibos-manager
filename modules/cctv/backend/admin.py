"""
CCTV Admin Configuration
Django admin interface for camera management
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Camera, CameraStream, RecordingSession, 
    RecordingSchedule, Alert, CameraGroup, StorageConfiguration
)


@admin.register(Camera)
class CameraAdmin(admin.ModelAdmin):
    """Camera administration"""
    list_display = [
        'name', 'location', 'model', 'ip_address', 
        'status_badge', 'is_active', 'recording_enabled'
    ]
    list_filter = ['status', 'is_active', 'model', 'recording_enabled']
    search_fields = ['name', 'location', 'ip_address']
    readonly_fields = ['id', 'created_at', 'updated_at', 'last_seen']
    
    fieldsets = (
        ('basic information', {
            'fields': ('name', 'model', 'location', 'description')
        }),
        ('network configuration', {
            'fields': ('ip_address', 'port', 'protocol', 'stream_path')
        }),
        ('authentication', {
            'fields': ('username', 'password'),
            'classes': ('collapse',)
        }),
        ('settings', {
            'fields': (
                'is_active', 'recording_enabled', 'motion_detection', 
                'audio_enabled', 'status'
            )
        }),
        ('video settings', {
            'fields': ('resolution', 'fps', 'bitrate')
        }),
        ('ptz configuration', {
            'fields': ('has_ptz', 'ptz_preset_positions'),
            'classes': ('collapse',)
        }),
        ('kerberos integration', {
            'fields': ('kerberos_enabled', 'kerberos_url', 'kerberos_key'),
            'classes': ('collapse',)
        }),
        ('metadata', {
            'fields': ('id', 'user', 'created_at', 'updated_at', 'last_seen'),
            'classes': ('collapse',)
        })
    )
    
    def status_badge(self, obj):
        """Display status as colored badge"""
        colors = {
            'online': 'green',
            'offline': 'red',
            'recording': 'orange',
            'error': 'red',
            'maintenance': 'gray'
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; '
            'border-radius: 3px; font-weight: bold;">{}</span>',
            color, obj.status
        )
    status_badge.short_description = 'status'


@admin.register(CameraStream)
class CameraStreamAdmin(admin.ModelAdmin):
    """Camera stream administration"""
    list_display = ['camera', 'quality', 'protocol', 'resolution', 'is_active']
    list_filter = ['quality', 'protocol', 'is_active']
    search_fields = ['camera__name']


@admin.register(RecordingSession)
class RecordingSessionAdmin(admin.ModelAdmin):
    """Recording session administration"""
    list_display = [
        'camera', 'recording_type', 'status', 
        'start_time', 'duration', 'file_size_mb'
    ]
    list_filter = ['status', 'recording_type', 'start_time']
    search_fields = ['camera__name']
    date_hierarchy = 'start_time'
    
    def file_size_mb(self, obj):
        """Display file size in MB"""
        if obj.file_size:
            return f"{obj.file_size / (1024*1024):.2f} MB"
        return "-"
    file_size_mb.short_description = 'file size'


@admin.register(RecordingSchedule)
class RecordingScheduleAdmin(admin.ModelAdmin):
    """Recording schedule administration"""
    list_display = [
        'name', 'camera', 'start_time', 'end_time', 
        'is_active', 'retention_days'
    ]
    list_filter = ['is_active', 'motion_only']
    search_fields = ['name', 'camera__name']


@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    """Alert administration"""
    list_display = [
        'camera', 'alert_type', 'priority_badge', 
        'timestamp', 'is_resolved', 'resolved_by'
    ]
    list_filter = ['alert_type', 'priority', 'is_resolved', 'timestamp']
    search_fields = ['camera__name', 'description']
    date_hierarchy = 'timestamp'
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    def priority_badge(self, obj):
        """Display priority as colored badge"""
        colors = {
            'low': 'green',
            'medium': 'orange',
            'high': 'red',
            'critical': 'darkred'
        }
        color = colors.get(obj.priority, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; '
            'border-radius: 3px; font-weight: bold;">{}</span>',
            color, obj.priority
        )
    priority_badge.short_description = 'priority'
    
    actions = ['mark_resolved']
    
    def mark_resolved(self, request, queryset):
        """Mark selected alerts as resolved"""
        count = queryset.filter(is_resolved=False).update(
            is_resolved=True,
            resolved_by=request.user
        )
        self.message_user(request, f"{count} alerts marked as resolved")
    mark_resolved.short_description = "mark selected alerts as resolved"


@admin.register(CameraGroup)
class CameraGroupAdmin(admin.ModelAdmin):
    """Camera group administration"""
    list_display = ['name', 'user', 'camera_count', 'grid_layout', 'auto_cycle']
    search_fields = ['name']
    filter_horizontal = ['cameras']
    
    def camera_count(self, obj):
        """Display number of cameras in group"""
        return obj.cameras.count()
    camera_count.short_description = 'cameras'


@admin.register(StorageConfiguration)
class StorageConfigurationAdmin(admin.ModelAdmin):
    """Storage configuration administration"""
    list_display = [
        'name', 'max_storage_gb', 'current_usage_gb', 
        'usage_percentage', 'is_active'
    ]
    readonly_fields = ['current_usage_gb', 'last_cleanup']
    
    def usage_percentage(self, obj):
        """Display storage usage percentage"""
        percent = obj.get_usage_percent()
        color = 'green' if percent < 60 else 'orange' if percent < 80 else 'red'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{:.1f}%</span>',
            color, percent
        )
    usage_percentage.short_description = 'usage'