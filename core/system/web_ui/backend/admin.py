"""
UNIBOS Web UI Admin Configuration
"""

from django.contrib import admin
from .models import SessionLog, ModuleAccess, UIPreferences, SystemStatus, CommandHistory


@admin.register(SessionLog)
class SessionLogAdmin(admin.ModelAdmin):
    list_display = ['session_id', 'user', 'ip_address', 'started_at', 'is_active']
    list_filter = ['is_active', 'started_at']
    search_fields = ['session_id', 'user__username', 'ip_address']
    readonly_fields = ['session_id', 'started_at']
    date_hierarchy = 'started_at'


@admin.register(ModuleAccess)
class ModuleAccessAdmin(admin.ModelAdmin):
    list_display = ['user', 'module', 'accessed_at', 'action']
    list_filter = ['module', 'accessed_at']
    search_fields = ['user__username', 'action']
    date_hierarchy = 'accessed_at'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'session')


@admin.register(UIPreferences)
class UIPreferencesAdmin(admin.ModelAdmin):
    list_display = ['user', 'theme', 'font_size', 'language', 'updated_at']
    list_filter = ['theme', 'language', 'show_animations', 'enable_sound']
    search_fields = ['user__username']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(SystemStatus)
class SystemStatusAdmin(admin.ModelAdmin):
    list_display = ['module', 'status', 'health_score', 'last_checked', 'error_count', 'warning_count']
    list_filter = ['status', 'module']
    search_fields = ['module']
    readonly_fields = ['last_checked']
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editing an existing object
            return self.readonly_fields + ['module']
        return self.readonly_fields


@admin.register(CommandHistory)
class CommandHistoryAdmin(admin.ModelAdmin):
    list_display = ['user', 'command_short', 'module', 'executed_at', 'success', 'execution_time']
    list_filter = ['success', 'module', 'executed_at']
    search_fields = ['user__username', 'command']
    date_hierarchy = 'executed_at'
    readonly_fields = ['executed_at']
    
    def command_short(self, obj):
        return obj.command[:50] + '...' if len(obj.command) > 50 else obj.command
    command_short.short_description = 'Command'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')