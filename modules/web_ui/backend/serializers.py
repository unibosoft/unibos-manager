"""
UNIBOS Web UI Serializers
"""

from rest_framework import serializers
from .models import SessionLog, ModuleAccess, UIPreferences, SystemStatus, CommandHistory


class SessionLogSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = SessionLog
        fields = ['id', 'session_id', 'username', 'ip_address', 'user_agent',
                  'started_at', 'ended_at', 'is_active']
        read_only_fields = ['session_id', 'started_at']


class ModuleAccessSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    module_display = serializers.CharField(source='get_module_display', read_only=True)
    
    class Meta:
        model = ModuleAccess
        fields = ['id', 'username', 'module', 'module_display', 'accessed_at',
                  'action', 'data']


class UIPreferencesSerializer(serializers.ModelSerializer):
    class Meta:
        model = UIPreferences
        fields = ['theme', 'font_size', 'show_animations', 'enable_sound',
                  'keyboard_shortcuts', 'auto_refresh', 'refresh_interval',
                  'sidebar_collapsed', 'language']


class SystemStatusSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = SystemStatus
        fields = ['id', 'module', 'status', 'status_display', 'health_score',
                  'last_checked', 'error_count', 'warning_count', 'metadata']
        read_only_fields = ['last_checked']


class CommandHistorySerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = CommandHistory
        fields = ['id', 'username', 'command', 'module', 'executed_at',
                  'success', 'output', 'error_message', 'execution_time']
        read_only_fields = ['executed_at']


class CommandExecuteSerializer(serializers.Serializer):
    """Serializer for executing commands"""
    command = serializers.CharField(required=True)
    module = serializers.CharField(required=False, allow_null=True)