"""
CCTV Serializers
REST API serializers for camera management
"""

from rest_framework import serializers
from .models import (
    Camera, CameraStream, RecordingSession,
    RecordingSchedule, Alert, CameraGroup, StorageConfiguration
)


class CameraStreamSerializer(serializers.ModelSerializer):
    """Camera stream serializer"""
    
    class Meta:
        model = CameraStream
        fields = [
            'id', 'camera', 'quality', 'protocol', 'stream_url',
            'is_active', 'resolution', 'fps', 'bitrate'
        ]
        read_only_fields = ['id']


class CameraSerializer(serializers.ModelSerializer):
    """Camera serializer"""
    streams = CameraStreamSerializer(many=True, read_only=True)
    rtsp_url = serializers.SerializerMethodField()
    snapshot_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Camera
        fields = [
            'id', 'name', 'model', 'location', 'description',
            'ip_address', 'port', 'protocol', 'stream_path',
            'status', 'is_active', 'recording_enabled',
            'motion_detection', 'audio_enabled',
            'resolution', 'fps', 'bitrate',
            'has_ptz', 'ptz_preset_positions',
            'kerberos_enabled', 'last_seen',
            'created_at', 'updated_at',
            'streams', 'rtsp_url', 'snapshot_url'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'last_seen']
        extra_kwargs = {
            'username': {'write_only': True},
            'password': {'write_only': True},
        }
    
    def get_rtsp_url(self, obj):
        """Get RTSP URL for streaming"""
        return obj.get_rtsp_url()
    
    def get_snapshot_url(self, obj):
        """Get snapshot URL"""
        return obj.get_snapshot_url()


class CameraCreateSerializer(serializers.ModelSerializer):
    """Camera creation serializer with credentials"""
    
    class Meta:
        model = Camera
        fields = [
            'name', 'model', 'location', 'description',
            'ip_address', 'port', 'protocol', 'stream_path',
            'username', 'password',
            'is_active', 'recording_enabled',
            'motion_detection', 'audio_enabled',
            'resolution', 'fps', 'bitrate',
            'has_ptz', 'kerberos_enabled',
            'kerberos_url', 'kerberos_key'
        ]
    
    def create(self, validated_data):
        """Create camera with user association"""
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class RecordingSessionSerializer(serializers.ModelSerializer):
    """Recording session serializer"""
    camera_name = serializers.CharField(source='camera.name', read_only=True)
    
    class Meta:
        model = RecordingSession
        fields = [
            'id', 'camera', 'camera_name', 'recording_type',
            'status', 'start_time', 'end_time', 'duration',
            'file_path', 'file_size', 'thumbnail_path',
            'video_codec', 'audio_codec', 'resolution', 'fps',
            'motion_events', 'notes',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'duration', 'file_path', 'file_size',
            'thumbnail_path', 'created_at', 'updated_at'
        ]


class RecordingScheduleSerializer(serializers.ModelSerializer):
    """Recording schedule serializer"""
    camera_name = serializers.CharField(source='camera.name', read_only=True)
    is_active_now = serializers.SerializerMethodField()
    
    class Meta:
        model = RecordingSchedule
        fields = [
            'id', 'camera', 'camera_name', 'name',
            'days_of_week', 'start_time', 'end_time',
            'is_active', 'recording_quality', 'motion_only',
            'retention_days', 'is_active_now',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_is_active_now(self, obj):
        """Check if schedule is currently active"""
        return obj.is_active_now()


class AlertSerializer(serializers.ModelSerializer):
    """Alert serializer"""
    camera_name = serializers.CharField(source='camera.name', read_only=True)
    camera_location = serializers.CharField(source='camera.location', read_only=True)
    
    class Meta:
        model = Alert
        fields = [
            'id', 'camera', 'camera_name', 'camera_location',
            'alert_type', 'priority', 'timestamp',
            'description', 'image_path', 'video_clip_path',
            'confidence_score', 'detection_data',
            'is_resolved', 'resolved_by', 'resolved_at',
            'resolution_notes', 'notification_sent',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'resolved_by', 'resolved_at',
            'notification_sent', 'notification_sent_at',
            'created_at', 'updated_at'
        ]


class AlertResolveSerializer(serializers.Serializer):
    """Serializer for resolving alerts"""
    resolution_notes = serializers.CharField(required=False, allow_blank=True)


class CameraGroupSerializer(serializers.ModelSerializer):
    """Camera group serializer"""
    cameras = CameraSerializer(many=True, read_only=True)
    camera_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        write_only=True,
        queryset=Camera.objects.all(),
        source='cameras'
    )
    
    class Meta:
        model = CameraGroup
        fields = [
            'id', 'name', 'description', 'cameras', 'camera_ids',
            'grid_layout', 'auto_cycle', 'cycle_interval',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        """Create camera group with user association"""
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class StorageConfigurationSerializer(serializers.ModelSerializer):
    """Storage configuration serializer"""
    usage_percent = serializers.SerializerMethodField()
    
    class Meta:
        model = StorageConfiguration
        fields = [
            'id', 'name', 'recording_path', 'snapshot_path',
            'max_storage_gb', 'warning_threshold_percent',
            'default_retention_days', 'auto_delete_old',
            'current_usage_gb', 'usage_percent', 'last_cleanup',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'current_usage_gb', 'last_cleanup',
            'created_at', 'updated_at'
        ]
    
    def get_usage_percent(self, obj):
        """Get storage usage percentage"""
        return obj.get_usage_percent()


class CameraStatusSerializer(serializers.Serializer):
    """Camera status update serializer"""
    status = serializers.ChoiceField(choices=Camera.CAMERA_STATUS)
    recording_enabled = serializers.BooleanField(required=False)
    motion_detection = serializers.BooleanField(required=False)
    audio_enabled = serializers.BooleanField(required=False)


class PTZControlSerializer(serializers.Serializer):
    """PTZ control command serializer"""
    command = serializers.ChoiceField(
        choices=['up', 'down', 'left', 'right', 'zoom_in', 'zoom_out', 'home']
    )
    speed = serializers.IntegerField(min_value=1, max_value=10, default=5)
    preset = serializers.IntegerField(required=False, min_value=1, max_value=10)