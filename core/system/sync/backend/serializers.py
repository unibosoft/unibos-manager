"""
Sync API Serializers
"""

from rest_framework import serializers
from .models import (
    SyncSession, SyncRecord, SyncConflict,
    OfflineOperation, VersionVector,
    SyncStatus, SyncDirection, ConflictStrategy,
    DataExportSettings, DataExportLog, ExportStatus, ExportDestination
)


class VersionVectorSerializer(serializers.ModelSerializer):
    """Serializer for version vectors"""

    class Meta:
        model = VersionVector
        fields = [
            'model_name', 'version', 'last_synced_version',
            'total_records', 'pending_changes', 'last_modified', 'last_synced'
        ]
        read_only_fields = fields


class SyncInitRequestSerializer(serializers.Serializer):
    """Request to initialize a sync session"""
    node_id = serializers.UUIDField()
    node_hostname = serializers.CharField(max_length=255)
    modules = serializers.ListField(
        child=serializers.CharField(max_length=50),
        required=False,
        default=list
    )
    version_vector = serializers.DictField(
        child=serializers.IntegerField(),
        required=False,
        default=dict
    )
    direction = serializers.ChoiceField(
        choices=SyncDirection.choices,
        default=SyncDirection.BIDIRECTIONAL
    )


class SyncInitResponseSerializer(serializers.Serializer):
    """Response from sync init"""
    session_id = serializers.UUIDField()
    hub_version_vector = serializers.DictField()
    changes_available = serializers.IntegerField()
    conflicts_detected = serializers.IntegerField()
    modules = serializers.ListField(child=serializers.CharField())


class SyncRecordSerializer(serializers.ModelSerializer):
    """Serializer for sync records"""

    class Meta:
        model = SyncRecord
        fields = [
            'id', 'model_name', 'record_id', 'operation',
            'data', 'checksum', 'local_version', 'remote_version',
            'status', 'local_modified_at', 'remote_modified_at',
            'synced_at', 'error_message'
        ]
        read_only_fields = ['id', 'synced_at', 'error_message']


class SyncPullRequestSerializer(serializers.Serializer):
    """Request to pull changes from Hub"""
    session_id = serializers.UUIDField()
    batch_size = serializers.IntegerField(default=100, min_value=1, max_value=1000)
    offset = serializers.IntegerField(default=0, min_value=0)
    models = serializers.ListField(
        child=serializers.CharField(max_length=100),
        required=False
    )


class SyncPullResponseSerializer(serializers.Serializer):
    """Response from sync pull"""
    records = SyncRecordSerializer(many=True)
    total_count = serializers.IntegerField()
    has_more = serializers.BooleanField()
    next_offset = serializers.IntegerField()


class SyncPushRequestSerializer(serializers.Serializer):
    """Request to push changes to Hub"""
    session_id = serializers.UUIDField()
    records = serializers.ListField(
        child=serializers.DictField(),
        min_length=1,
        max_length=1000
    )


class SyncPushResponseSerializer(serializers.Serializer):
    """Response from sync push"""
    accepted = serializers.IntegerField()
    rejected = serializers.IntegerField()
    conflicts = serializers.IntegerField()
    errors = serializers.ListField(child=serializers.DictField())


class SyncConflictSerializer(serializers.ModelSerializer):
    """Serializer for sync conflicts"""

    class Meta:
        model = SyncConflict
        fields = [
            'id', 'model_name', 'record_id',
            'local_data', 'remote_data',
            'local_modified_at', 'remote_modified_at',
            'local_node_id', 'remote_source',
            'strategy', 'resolved', 'resolution_data',
            'resolved_by', 'resolved_at', 'detected_at'
        ]
        read_only_fields = ['id', 'detected_at']


class ConflictResolveRequestSerializer(serializers.Serializer):
    """Request to resolve a conflict"""
    conflict_id = serializers.UUIDField()
    strategy = serializers.ChoiceField(choices=ConflictStrategy.choices)
    resolution_data = serializers.DictField(required=False)


class SyncSessionSerializer(serializers.ModelSerializer):
    """Serializer for sync sessions"""
    progress_percent = serializers.IntegerField(read_only=True)

    class Meta:
        model = SyncSession
        fields = [
            'id', 'node_id', 'node_hostname', 'direction', 'status',
            'modules', 'node_version_vector', 'hub_version_vector',
            'total_records', 'processed_records', 'conflicts_count',
            'progress_percent', 'created_at', 'started_at', 'completed_at',
            'last_error', 'retry_count'
        ]
        read_only_fields = fields


class OfflineOperationSerializer(serializers.ModelSerializer):
    """Serializer for offline operations"""

    class Meta:
        model = OfflineOperation
        fields = [
            'id', 'node_id', 'operation_type', 'module',
            'target_url', 'method', 'payload', 'headers',
            'priority', 'status', 'retry_count', 'max_retries',
            'created_at', 'scheduled_for', 'last_attempt',
            'completed_at', 'last_error', 'expires_at'
        ]
        read_only_fields = ['id', 'created_at', 'last_attempt', 'completed_at']


class SyncStatusSerializer(serializers.Serializer):
    """Overall sync status for a node"""
    node_id = serializers.UUIDField()
    is_synced = serializers.BooleanField()
    last_sync = serializers.DateTimeField(allow_null=True)
    pending_push = serializers.IntegerField()
    pending_pull = serializers.IntegerField()
    unresolved_conflicts = serializers.IntegerField()
    offline_operations = serializers.IntegerField()
    version_vectors = VersionVectorSerializer(many=True)


# =============================================================================
# DATA EXPORT CONTROL SERIALIZERS
# =============================================================================

class DataExportSettingsSerializer(serializers.ModelSerializer):
    """Serializer for export settings"""

    class Meta:
        model = DataExportSettings
        fields = [
            'id', 'node_id', 'node_hostname',
            'master_kill_switch', 'module_settings',
            'new_modules_default_export', 'require_confirmation',
            'confirmation_timeout_seconds', 'log_all_exports',
            'log_blocked_exports', 'allow_local_mesh',
            'emergency_bypass', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ExportSettingsUpdateSerializer(serializers.Serializer):
    """Request to update export settings"""
    master_kill_switch = serializers.BooleanField(required=False)
    module_settings = serializers.DictField(required=False)
    new_modules_default_export = serializers.BooleanField(required=False)
    require_confirmation = serializers.BooleanField(required=False)
    log_all_exports = serializers.BooleanField(required=False)
    log_blocked_exports = serializers.BooleanField(required=False)
    allow_local_mesh = serializers.BooleanField(required=False)
    emergency_bypass = serializers.ListField(
        child=serializers.CharField(),
        required=False
    )


class ModulePermissionSerializer(serializers.Serializer):
    """Request to set module permission"""
    module = serializers.CharField(max_length=50)
    data_type = serializers.CharField(max_length=100, required=False, allow_null=True)
    allowed = serializers.BooleanField()


class KillSwitchSerializer(serializers.Serializer):
    """Request to toggle kill switch"""
    enabled = serializers.BooleanField()


class DataExportLogSerializer(serializers.ModelSerializer):
    """Serializer for export logs"""

    class Meta:
        model = DataExportLog
        fields = [
            'id', 'node_id', 'module', 'data_type', 'model_name',
            'destination_type', 'destination_id', 'destination_name',
            'status', 'blocked_reason', 'record_count', 'size_bytes',
            'request_path', 'request_method', 'user_id', 'user_ip',
            'timestamp', 'extra_data'
        ]
        read_only_fields = fields


class ExportStatsSerializer(serializers.Serializer):
    """Export statistics"""
    total = serializers.IntegerField()
    allowed = serializers.IntegerField()
    blocked = serializers.IntegerField()
    by_module = serializers.DictField()
    by_destination = serializers.DictField()
    total_records = serializers.IntegerField()
    total_bytes = serializers.IntegerField()


class ExportCheckRequestSerializer(serializers.Serializer):
    """Request to check if export is allowed"""
    module = serializers.CharField(max_length=50)
    data_type = serializers.CharField(max_length=100, required=False)


class ExportCheckResponseSerializer(serializers.Serializer):
    """Response for export check"""
    allowed = serializers.BooleanField()
    reason = serializers.CharField(allow_blank=True)
    kill_switch_active = serializers.BooleanField()
    module_allowed = serializers.BooleanField()
