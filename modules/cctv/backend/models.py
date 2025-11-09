"""
CCTV Models
Professional security camera management with TP-Link Tapo and Kerberos integration
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
# from django.contrib.postgres.fields import ArrayField  # PostgreSQL specific
import uuid
from pathlib import Path

User = get_user_model()


class Camera(models.Model):
    """Security camera configuration and management"""
    
    CAMERA_STATUS = [
        ('online', 'online'),
        ('offline', 'offline'),
        ('recording', 'recording'),
        ('error', 'error'),
        ('maintenance', 'maintenance'),
    ]
    
    CAMERA_MODELS = [
        ('tapo_c200', 'tp-link tapo c200'),
        ('tapo_c210', 'tp-link tapo c210'),
        ('tapo_c310', 'tp-link tapo c310'),
        ('tapo_c320ws', 'tp-link tapo c320ws'),
        ('generic_rtsp', 'generic rtsp camera'),
        ('onvif', 'onvif compatible'),
    ]
    
    PROTOCOLS = [
        ('rtsp', 'rtsp'),
        ('http', 'http'),
        ('https', 'https'),
        ('onvif', 'onvif'),
    ]
    
    # Basic Information
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, help_text="camera display name")
    model = models.CharField(max_length=50, choices=CAMERA_MODELS, default='tapo_c200')
    location = models.CharField(max_length=200, help_text="physical location")
    description = models.TextField(blank=True, help_text="additional notes")
    
    # Network Configuration
    ip_address = models.GenericIPAddressField(help_text="camera ip address")
    port = models.IntegerField(
        default=554,
        validators=[MinValueValidator(1), MaxValueValidator(65535)],
        help_text="rtsp/http port (default: 554 for rtsp)"
    )
    protocol = models.CharField(max_length=10, choices=PROTOCOLS, default='rtsp')
    stream_path = models.CharField(
        max_length=200,
        default='/stream1',
        help_text="stream path (e.g., /stream1 for main, /stream2 for sub)"
    )
    
    # Authentication
    username = models.CharField(max_length=100, help_text="camera username")
    password = models.CharField(max_length=100, help_text="camera password (encrypted in production)")
    
    # Status and Settings
    status = models.CharField(max_length=20, choices=CAMERA_STATUS, default='offline')
    is_active = models.BooleanField(default=True, help_text="camera enabled/disabled")
    recording_enabled = models.BooleanField(default=False, help_text="continuous recording")
    motion_detection = models.BooleanField(default=True, help_text="motion detection enabled")
    audio_enabled = models.BooleanField(default=False, help_text="audio recording enabled")
    
    # Video Settings
    resolution = models.CharField(
        max_length=20,
        default='1920x1080',
        help_text="video resolution"
    )
    fps = models.IntegerField(
        default=25,
        validators=[MinValueValidator(1), MaxValueValidator(60)],
        help_text="frames per second"
    )
    bitrate = models.IntegerField(
        default=2048,
        validators=[MinValueValidator(128), MaxValueValidator(8192)],
        help_text="video bitrate in kbps"
    )
    
    # PTZ (Pan-Tilt-Zoom) Support
    has_ptz = models.BooleanField(default=False, help_text="camera has ptz controls")
    ptz_preset_positions = models.JSONField(
        default=dict,
        blank=True,
        help_text="saved ptz positions"
    )
    
    # Kerberos Integration
    kerberos_enabled = models.BooleanField(default=False, help_text="use kerberos.io for processing")
    kerberos_url = models.URLField(blank=True, help_text="kerberos instance url")
    kerberos_key = models.CharField(max_length=100, blank=True, help_text="kerberos api key")
    
    # Metadata
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cameras')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_seen = models.DateTimeField(null=True, blank=True, help_text="last successful connection")
    
    class Meta:
        ordering = ['location', 'name']
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.location})"
    
    def get_rtsp_url(self):
        """Generate RTSP URL for the camera"""
        if self.protocol == 'rtsp':
            return f"rtsp://{self.username}:{self.password}@{self.ip_address}:{self.port}{self.stream_path}"
        return None
    
    def get_snapshot_url(self):
        """Generate snapshot URL for the camera"""
        if self.model.startswith('tapo'):
            return f"http://{self.username}:{self.password}@{self.ip_address}/cgi-bin/snapshot.cgi"
        return None


class CameraStream(models.Model):
    """Camera stream configurations for multiple quality levels"""
    
    STREAM_QUALITY = [
        ('main', 'main stream (high quality)'),
        ('sub', 'sub stream (low quality)'),
        ('mobile', 'mobile stream (optimized)'),
    ]
    
    STREAM_PROTOCOL = [
        ('rtsp', 'rtsp'),
        ('rtmp', 'rtmp'),
        ('hls', 'hls'),
        ('webrtc', 'webrtc'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    camera = models.ForeignKey(Camera, on_delete=models.CASCADE, related_name='streams')
    quality = models.CharField(max_length=20, choices=STREAM_QUALITY, default='main')
    protocol = models.CharField(max_length=20, choices=STREAM_PROTOCOL, default='rtsp')
    stream_url = models.TextField(help_text="full stream url")
    is_active = models.BooleanField(default=True)
    
    # Stream settings
    resolution = models.CharField(max_length=20, default='1920x1080')
    fps = models.IntegerField(default=25)
    bitrate = models.IntegerField(default=2048, help_text="kbps")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['camera', 'quality']
        ordering = ['camera', 'quality']
    
    def __str__(self):
        return f"{self.camera.name} - {self.quality}"


class RecordingSession(models.Model):
    """Recording session management for cameras"""
    
    RECORDING_STATUS = [
        ('scheduled', 'scheduled'),
        ('recording', 'recording'),
        ('completed', 'completed'),
        ('failed', 'failed'),
        ('processing', 'processing'),
    ]
    
    RECORDING_TYPE = [
        ('continuous', 'continuous'),
        ('motion', 'motion triggered'),
        ('manual', 'manual'),
        ('scheduled', 'scheduled'),
        ('alert', 'alert triggered'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    camera = models.ForeignKey(Camera, on_delete=models.CASCADE, related_name='recordings')
    
    # Recording details
    recording_type = models.CharField(max_length=20, choices=RECORDING_TYPE, default='manual')
    status = models.CharField(max_length=20, choices=RECORDING_STATUS, default='scheduled')
    
    # Time information
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)
    duration = models.IntegerField(null=True, blank=True, help_text="duration in seconds")
    
    # File information
    file_path = models.FilePathField(
        path='/media/cctv/recordings',
        blank=True,
        help_text="recording file path"
    )
    file_size = models.BigIntegerField(null=True, blank=True, help_text="file size in bytes")
    thumbnail_path = models.FilePathField(
        path='/media/cctv/thumbnails',
        blank=True,
        help_text="thumbnail image path"
    )
    
    # Video metadata
    video_codec = models.CharField(max_length=50, default='h264')
    audio_codec = models.CharField(max_length=50, blank=True)
    resolution = models.CharField(max_length=20, blank=True)
    fps = models.IntegerField(null=True, blank=True)
    
    # Additional metadata
    motion_events = models.IntegerField(default=0, help_text="number of motion events detected")
    notes = models.TextField(blank=True)
    
    # User tracking
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recordings')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-start_time']
        indexes = [
            models.Index(fields=['camera', 'start_time']),
            models.Index(fields=['status']),
            models.Index(fields=['recording_type']),
        ]
    
    def __str__(self):
        return f"{self.camera.name} - {self.start_time}"
    
    def calculate_duration(self):
        """Calculate recording duration"""
        if self.end_time and self.start_time:
            delta = self.end_time - self.start_time
            self.duration = int(delta.total_seconds())
            return self.duration
        return None


class RecordingSchedule(models.Model):
    """Schedule for automatic recordings"""
    
    DAYS_OF_WEEK = [
        (0, 'monday'),
        (1, 'tuesday'),
        (2, 'wednesday'),
        (3, 'thursday'),
        (4, 'friday'),
        (5, 'saturday'),
        (6, 'sunday'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    camera = models.ForeignKey(Camera, on_delete=models.CASCADE, related_name='schedules')
    name = models.CharField(max_length=100, help_text="schedule name")
    
    # Schedule configuration - Using JSONField for SQLite compatibility
    days_of_week = models.JSONField(
        default=list,
        help_text="days when recording is active (list of integers 0-6)"
    )
    start_time = models.TimeField(help_text="daily start time")
    end_time = models.TimeField(help_text="daily end time")
    
    # Settings
    is_active = models.BooleanField(default=True)
    recording_quality = models.CharField(
        max_length=20,
        choices=[('main', 'high quality'), ('sub', 'low quality')],
        default='main'
    )
    motion_only = models.BooleanField(default=False, help_text="record only on motion")
    
    # Retention
    retention_days = models.IntegerField(
        default=7,
        validators=[MinValueValidator(1), MaxValueValidator(365)],
        help_text="days to keep recordings"
    )
    
    # Metadata
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recording_schedules')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['camera', 'start_time']
    
    def __str__(self):
        return f"{self.camera.name} - {self.name}"
    
    def is_active_now(self):
        """Check if schedule is active at current time"""
        if not self.is_active:
            return False
        
        now = timezone.now()
        current_day = now.weekday()
        current_time = now.time()
        
        if current_day not in self.days_of_week:
            return False
        
        return self.start_time <= current_time <= self.end_time


class Alert(models.Model):
    """Security alerts and notifications"""
    
    ALERT_TYPE = [
        ('motion', 'motion detected'),
        ('sound', 'sound detected'),
        ('person', 'person detected'),
        ('vehicle', 'vehicle detected'),
        ('animal', 'animal detected'),
        ('package', 'package detected'),
        ('tampering', 'camera tampering'),
        ('connection_lost', 'connection lost'),
        ('storage_full', 'storage full'),
        ('system', 'system alert'),
    ]
    
    ALERT_PRIORITY = [
        ('low', 'low'),
        ('medium', 'medium'),
        ('high', 'high'),
        ('critical', 'critical'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    camera = models.ForeignKey(Camera, on_delete=models.CASCADE, related_name='alerts')
    
    # Alert details
    alert_type = models.CharField(max_length=30, choices=ALERT_TYPE)
    priority = models.CharField(max_length=20, choices=ALERT_PRIORITY, default='medium')
    timestamp = models.DateTimeField(default=timezone.now)
    
    # Alert content
    description = models.TextField(help_text="alert description")
    image_path = models.FilePathField(
        path='/media/cctv/alerts',
        blank=True,
        help_text="snapshot at alert time"
    )
    video_clip_path = models.FilePathField(
        path='/media/cctv/alerts',
        blank=True,
        help_text="short video clip of event"
    )
    
    # Detection metadata
    confidence_score = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text="ai detection confidence (0-1)"
    )
    detection_data = models.JSONField(
        default=dict,
        blank=True,
        help_text="additional detection metadata"
    )
    
    # Resolution
    is_resolved = models.BooleanField(default=False)
    resolved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='resolved_alerts'
    )
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolution_notes = models.TextField(blank=True)
    
    # Notification tracking
    notification_sent = models.BooleanField(default=False)
    notification_sent_at = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cctv_alerts')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-timestamp', '-priority']
        indexes = [
            models.Index(fields=['camera', 'timestamp']),
            models.Index(fields=['alert_type', 'is_resolved']),
            models.Index(fields=['priority', 'is_resolved']),
        ]
    
    def __str__(self):
        return f"{self.camera.name} - {self.alert_type} - {self.timestamp}"
    
    def resolve(self, user, notes=''):
        """Mark alert as resolved"""
        self.is_resolved = True
        self.resolved_by = user
        self.resolved_at = timezone.now()
        self.resolution_notes = notes
        self.save()


class CameraGroup(models.Model):
    """Group cameras for organized viewing"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    cameras = models.ManyToManyField(Camera, related_name='groups')
    
    # Display settings
    grid_layout = models.CharField(
        max_length=10,
        default='2x2',
        help_text="grid layout (e.g., 2x2, 3x3, 4x4)"
    )
    auto_cycle = models.BooleanField(default=False, help_text="auto cycle through cameras")
    cycle_interval = models.IntegerField(
        default=10,
        validators=[MinValueValidator(5), MaxValueValidator(300)],
        help_text="seconds between camera switches"
    )
    
    # Metadata
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='camera_groups')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        unique_together = ['user', 'name']
    
    def __str__(self):
        return self.name


class StorageConfiguration(models.Model):
    """Storage configuration for recordings"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    
    # Storage paths
    recording_path = models.CharField(
        max_length=500,
        default='/media/cctv/recordings',
        help_text="path for storing recordings"
    )
    snapshot_path = models.CharField(
        max_length=500,
        default='/media/cctv/snapshots',
        help_text="path for storing snapshots"
    )
    
    # Storage limits
    max_storage_gb = models.IntegerField(
        default=100,
        validators=[MinValueValidator(1)],
        help_text="maximum storage in gb"
    )
    warning_threshold_percent = models.IntegerField(
        default=80,
        validators=[MinValueValidator(1), MaxValueValidator(99)],
        help_text="warning when storage reaches this percentage"
    )
    
    # Retention policies
    default_retention_days = models.IntegerField(
        default=7,
        validators=[MinValueValidator(1), MaxValueValidator(365)],
        help_text="default days to keep recordings"
    )
    auto_delete_old = models.BooleanField(
        default=True,
        help_text="automatically delete old recordings"
    )
    
    # Current usage
    current_usage_gb = models.FloatField(default=0.0)
    last_cleanup = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def get_usage_percent(self):
        """Calculate storage usage percentage"""
        if self.max_storage_gb > 0:
            return (self.current_usage_gb / self.max_storage_gb) * 100
        return 0