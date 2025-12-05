"""
Sync Engine Models for UNIBOS

Handles data synchronization between Nodes and Hub.
Includes version vectors, offline queue, and conflict tracking.
"""

import uuid
import hashlib
import json
from django.db import models
from django.utils import timezone
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from datetime import timedelta


class SyncStatus(models.TextChoices):
    """Sync operation status"""
    PENDING = 'pending', 'Pending'
    IN_PROGRESS = 'in_progress', 'In Progress'
    COMPLETED = 'completed', 'Completed'
    FAILED = 'failed', 'Failed'
    CANCELLED = 'cancelled', 'Cancelled'
    CONFLICT = 'conflict', 'Has Conflicts'


class SyncDirection(models.TextChoices):
    """Sync direction"""
    PUSH = 'push', 'Push to Hub'
    PULL = 'pull', 'Pull from Hub'
    BIDIRECTIONAL = 'bidirectional', 'Bidirectional'


class ConflictStrategy(models.TextChoices):
    """Conflict resolution strategy"""
    NEWER_WINS = 'newer_wins', 'Newer Wins'
    OLDER_WINS = 'older_wins', 'Older Wins'
    HUB_WINS = 'hub_wins', 'Hub Wins'
    NODE_WINS = 'node_wins', 'Node Wins'
    MANUAL = 'manual', 'Manual Resolution'
    MERGE = 'merge', 'Merge Fields'
    KEEP_BOTH = 'keep_both', 'Keep Both'


class SyncSession(models.Model):
    """
    Represents a single sync session between Node and Hub.

    Each sync operation creates a session to track progress and handle
    interruptions gracefully.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Node identification
    node_id = models.UUIDField(db_index=True)
    node_hostname = models.CharField(max_length=255)

    # Session info
    direction = models.CharField(
        max_length=20,
        choices=SyncDirection.choices,
        default=SyncDirection.BIDIRECTIONAL
    )
    status = models.CharField(
        max_length=20,
        choices=SyncStatus.choices,
        default=SyncStatus.PENDING
    )

    # Modules being synced
    modules = models.JSONField(default=list)  # ['currencies', 'documents', ...]

    # Version tracking
    node_version_vector = models.JSONField(default=dict)  # {model: version, ...}
    hub_version_vector = models.JSONField(default=dict)

    # Progress tracking
    total_records = models.IntegerField(default=0)
    processed_records = models.IntegerField(default=0)
    conflicts_count = models.IntegerField(default=0)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    # Error handling
    last_error = models.TextField(blank=True)
    retry_count = models.IntegerField(default=0)

    class Meta:
        db_table = 'sync_sessions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['node_id', 'status']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"Sync {self.id} - {self.node_hostname} ({self.status})"

    def start(self):
        """Mark session as started"""
        self.status = SyncStatus.IN_PROGRESS
        self.started_at = timezone.now()
        self.save(update_fields=['status', 'started_at'])

    def complete(self):
        """Mark session as completed"""
        self.status = SyncStatus.COMPLETED
        self.completed_at = timezone.now()
        self.save(update_fields=['status', 'completed_at'])

    def fail(self, error_message):
        """Mark session as failed"""
        self.status = SyncStatus.FAILED
        self.last_error = error_message
        self.completed_at = timezone.now()
        self.save(update_fields=['status', 'last_error', 'completed_at'])

    @property
    def progress_percent(self):
        if self.total_records == 0:
            return 0
        return int((self.processed_records / self.total_records) * 100)


class SyncRecord(models.Model):
    """
    Individual record change to be synced.

    Tracks each record that needs to be pushed or pulled during sync.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Session reference
    session = models.ForeignKey(
        SyncSession,
        on_delete=models.CASCADE,
        related_name='records'
    )

    # Record identification
    model_name = models.CharField(max_length=100, db_index=True)  # 'currencies.Portfolio'
    record_id = models.CharField(max_length=100, db_index=True)   # UUID or PK

    # Change type
    operation = models.CharField(
        max_length=10,
        choices=[
            ('create', 'Create'),
            ('update', 'Update'),
            ('delete', 'Delete'),
        ]
    )

    # Data
    data = models.JSONField(default=dict)
    checksum = models.CharField(max_length=64)  # SHA256 of data

    # Version info
    local_version = models.BigIntegerField(default=0)
    remote_version = models.BigIntegerField(default=0)

    # Status
    status = models.CharField(
        max_length=20,
        choices=SyncStatus.choices,
        default=SyncStatus.PENDING
    )

    # Timestamps
    local_modified_at = models.DateTimeField()
    remote_modified_at = models.DateTimeField(null=True, blank=True)
    synced_at = models.DateTimeField(null=True, blank=True)

    # Error
    error_message = models.TextField(blank=True)

    class Meta:
        db_table = 'sync_records'
        ordering = ['model_name', 'record_id']
        indexes = [
            models.Index(fields=['session', 'status']),
            models.Index(fields=['model_name', 'record_id']),
        ]

    def __str__(self):
        return f"{self.operation} {self.model_name}:{self.record_id}"

    def compute_checksum(self):
        """Compute SHA256 checksum of data"""
        data_str = json.dumps(self.data, sort_keys=True, default=str)
        return hashlib.sha256(data_str.encode()).hexdigest()

    def save(self, *args, **kwargs):
        if not self.checksum:
            self.checksum = self.compute_checksum()
        super().save(*args, **kwargs)


class SyncConflict(models.Model):
    """
    Data conflict between Node and Hub.

    Created when the same record is modified on both sides since last sync.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Session reference
    session = models.ForeignKey(
        SyncSession,
        on_delete=models.CASCADE,
        related_name='conflicts',
        null=True,
        blank=True
    )

    # Record identification
    model_name = models.CharField(max_length=100, db_index=True)
    record_id = models.CharField(max_length=100, db_index=True)

    # Conflicting data
    local_data = models.JSONField()
    remote_data = models.JSONField()

    # Timestamps
    local_modified_at = models.DateTimeField()
    remote_modified_at = models.DateTimeField()

    # Source info
    local_node_id = models.UUIDField()
    remote_source = models.CharField(max_length=100)  # 'hub' or node UUID

    # Resolution
    strategy = models.CharField(
        max_length=20,
        choices=ConflictStrategy.choices,
        default=ConflictStrategy.MANUAL
    )
    resolved = models.BooleanField(default=False)
    resolution_data = models.JSONField(null=True, blank=True)
    resolved_by = models.UUIDField(null=True, blank=True)  # User UUID
    resolved_at = models.DateTimeField(null=True, blank=True)

    # Timestamps
    detected_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'sync_conflicts'
        ordering = ['-detected_at']
        indexes = [
            models.Index(fields=['model_name', 'record_id']),
            models.Index(fields=['resolved', 'detected_at']),
        ]

    def __str__(self):
        status = "Resolved" if self.resolved else "Pending"
        return f"Conflict: {self.model_name}:{self.record_id} ({status})"

    def resolve(self, strategy, resolved_data, user_id=None):
        """Resolve the conflict"""
        self.strategy = strategy
        self.resolution_data = resolved_data
        self.resolved = True
        self.resolved_by = user_id
        self.resolved_at = timezone.now()
        self.save()


class OfflineOperation(models.Model):
    """
    Operations queued for when connectivity returns.

    When Node can't reach Hub, operations are queued here and
    processed when connection is restored.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Node identification
    node_id = models.UUIDField(db_index=True)

    # Operation type
    operation_type = models.CharField(
        max_length=50,
        choices=[
            ('hub_sync', 'Hub Sync'),
            ('hub_auth', 'Hub Authentication'),
            ('node_sync', 'Node-to-Node Sync'),
            ('api_call', 'External API Call'),
            ('webhook', 'Webhook Delivery'),
        ]
    )

    # Target
    module = models.CharField(max_length=50, blank=True)
    target_url = models.URLField(blank=True)

    # Payload
    method = models.CharField(max_length=10, default='POST')
    payload = models.JSONField(default=dict)
    headers = models.JSONField(default=dict)

    # Priority (1 = highest)
    PRIORITY_CRITICAL = 1
    PRIORITY_HIGH = 2
    PRIORITY_NORMAL = 5
    PRIORITY_LOW = 8
    PRIORITY_BACKGROUND = 10

    priority = models.IntegerField(default=5)

    # Status
    status = models.CharField(
        max_length=20,
        choices=SyncStatus.choices,
        default=SyncStatus.PENDING
    )

    # Retry handling
    retry_count = models.IntegerField(default=0)
    max_retries = models.IntegerField(default=5)
    retry_delay_seconds = models.IntegerField(default=60)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    scheduled_for = models.DateTimeField(default=timezone.now)
    last_attempt = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    # Error tracking
    last_error = models.TextField(blank=True)

    # Expiration (optional)
    expires_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'sync_offline_operations'
        ordering = ['priority', 'created_at']
        indexes = [
            models.Index(fields=['node_id', 'status']),
            models.Index(fields=['priority', 'scheduled_for']),
            models.Index(fields=['operation_type', 'status']),
        ]

    def __str__(self):
        return f"{self.operation_type} ({self.status}) - Priority {self.priority}"

    def can_retry(self):
        """Check if operation can be retried"""
        if self.retry_count >= self.max_retries:
            return False
        if self.expires_at and timezone.now() > self.expires_at:
            return False
        return True

    def schedule_retry(self):
        """Schedule next retry with exponential backoff"""
        if not self.can_retry():
            self.status = SyncStatus.FAILED
            self.save(update_fields=['status'])
            return False

        self.retry_count += 1
        delay = self.retry_delay_seconds * (2 ** (self.retry_count - 1))
        self.scheduled_for = timezone.now() + timedelta(seconds=delay)
        self.status = SyncStatus.PENDING
        self.save(update_fields=['retry_count', 'scheduled_for', 'status'])
        return True

    def mark_completed(self):
        """Mark operation as completed"""
        self.status = SyncStatus.COMPLETED
        self.completed_at = timezone.now()
        self.save(update_fields=['status', 'completed_at'])

    def mark_failed(self, error_message):
        """Mark operation as failed"""
        self.last_error = error_message
        self.last_attempt = timezone.now()
        self.save(update_fields=['last_error', 'last_attempt'])
        return self.schedule_retry()

    @classmethod
    def get_pending(cls, node_id=None, limit=100):
        """Get pending operations ready to execute"""
        queryset = cls.objects.filter(
            status=SyncStatus.PENDING,
            scheduled_for__lte=timezone.now()
        )
        if node_id:
            queryset = queryset.filter(node_id=node_id)
        return queryset[:limit]

    @classmethod
    def cleanup_completed(cls, days=7):
        """Remove old completed operations"""
        cutoff = timezone.now() - timedelta(days=days)
        return cls.objects.filter(
            status=SyncStatus.COMPLETED,
            completed_at__lt=cutoff
        ).delete()


class VersionVector(models.Model):
    """
    Version tracking for syncable models.

    Stores the current sync version for each model on each node.
    Used to calculate diffs during sync.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Node identification
    node_id = models.UUIDField(db_index=True)

    # Model tracking
    model_name = models.CharField(max_length=100, db_index=True)  # 'currencies.Portfolio'

    # Version info
    version = models.BigIntegerField(default=0)
    last_synced_version = models.BigIntegerField(default=0)

    # Record counts
    total_records = models.IntegerField(default=0)
    pending_changes = models.IntegerField(default=0)

    # Timestamps
    last_modified = models.DateTimeField(auto_now=True)
    last_synced = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'sync_version_vectors'
        unique_together = ['node_id', 'model_name']
        indexes = [
            models.Index(fields=['node_id']),
            models.Index(fields=['model_name']),
        ]

    def __str__(self):
        return f"{self.model_name} v{self.version} (Node: {self.node_id})"

    def increment(self):
        """Increment version on change"""
        self.version += 1
        self.pending_changes += 1
        self.save(update_fields=['version', 'pending_changes', 'last_modified'])

    def mark_synced(self):
        """Mark as synced"""
        self.last_synced_version = self.version
        self.pending_changes = 0
        self.last_synced = timezone.now()
        self.save(update_fields=['last_synced_version', 'pending_changes', 'last_synced'])

    @classmethod
    def get_or_create_for_model(cls, node_id, model_name):
        """Get or create version vector for a model"""
        obj, created = cls.objects.get_or_create(
            node_id=node_id,
            model_name=model_name,
            defaults={'version': 0, 'last_synced_version': 0}
        )
        return obj


class SyncableModelMixin(models.Model):
    """
    Mixin for models that need to be synced between Node and Hub.

    Add this mixin to any model that should participate in sync.

    Usage:
        class Portfolio(SyncableModelMixin, models.Model):
            # your fields here
            pass
    """
    # Sync metadata
    sync_version = models.BigIntegerField(default=0, db_index=True)
    sync_checksum = models.CharField(max_length=64, blank=True)
    sync_status = models.CharField(
        max_length=20,
        choices=[
            ('synced', 'Synced'),
            ('pending', 'Pending Sync'),
            ('conflict', 'Has Conflict'),
        ],
        default='pending'
    )

    # Origin tracking
    origin_node_id = models.UUIDField(null=True, blank=True, db_index=True)

    # Timestamps for sync
    local_created_at = models.DateTimeField(auto_now_add=True)
    local_modified_at = models.DateTimeField(auto_now=True)
    synced_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True

    def get_sync_data(self):
        """
        Override this method to customize which fields are synced.
        Returns a dict of field names and values.
        """
        data = {}
        for field in self._meta.fields:
            if field.name not in ['sync_version', 'sync_checksum', 'sync_status',
                                   'synced_at', 'local_created_at', 'local_modified_at']:
                value = getattr(self, field.name)
                # Handle special types
                if hasattr(value, 'isoformat'):
                    value = value.isoformat()
                elif hasattr(value, 'hex'):  # UUID
                    value = str(value)
                data[field.name] = value
        return data

    def compute_sync_checksum(self):
        """Compute checksum of syncable data"""
        data = self.get_sync_data()
        data_str = json.dumps(data, sort_keys=True, default=str)
        return hashlib.sha256(data_str.encode()).hexdigest()

    def mark_for_sync(self):
        """Mark record as needing sync"""
        self.sync_version += 1
        self.sync_checksum = self.compute_sync_checksum()
        self.sync_status = 'pending'
        self.save(update_fields=['sync_version', 'sync_checksum', 'sync_status', 'local_modified_at'])

    def mark_synced(self):
        """Mark record as synced"""
        self.sync_status = 'synced'
        self.synced_at = timezone.now()
        self.save(update_fields=['sync_status', 'synced_at'])

    def save(self, *args, **kwargs):
        # Auto-compute checksum on save if data changed
        if not kwargs.get('update_fields'):
            new_checksum = self.compute_sync_checksum()
            if new_checksum != self.sync_checksum:
                self.sync_checksum = new_checksum
                self.sync_version += 1
                self.sync_status = 'pending'
        super().save(*args, **kwargs)


# =============================================================================
# DATA EXPORT CONTROL
# =============================================================================

class DataExportSettings(models.Model):
    """
    Data export control settings per node.

    Controls what data can leave the node - the master kill switch
    and granular module-level permissions.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Node identification
    node_id = models.UUIDField(unique=True, db_index=True)
    node_hostname = models.CharField(max_length=255, blank=True)

    # Master kill switch - when ON, NO data leaves the node
    master_kill_switch = models.BooleanField(default=False)

    # Module-level export settings
    # Format: {"currencies": {"portfolio": true, "transactions": false}, ...}
    module_settings = models.JSONField(default=dict)

    # Default behavior for new modules
    new_modules_default_export = models.BooleanField(default=False)

    # Confirmation settings
    require_confirmation = models.BooleanField(default=True)
    confirmation_timeout_seconds = models.IntegerField(default=30)

    # Logging
    log_all_exports = models.BooleanField(default=True)
    log_blocked_exports = models.BooleanField(default=True)

    # Local mesh exception - allow P2P even when kill switch is on
    allow_local_mesh = models.BooleanField(default=True)

    # Emergency bypass - these data types always receive data
    # e.g., ["birlikteyiz.earthquake_alerts"]
    emergency_bypass = models.JSONField(default=list)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'export_settings'
        verbose_name = 'Data Export Settings'
        verbose_name_plural = 'Data Export Settings'

    def __str__(self):
        status = "BLOCKED" if self.master_kill_switch else "ALLOWED"
        return f"Export Settings for {self.node_hostname} ({status})"

    def can_export(self, module, data_type=None):
        """
        Check if export is allowed for a module/data_type.

        Args:
            module: Module name (e.g., 'currencies')
            data_type: Optional data type within module (e.g., 'portfolio')

        Returns:
            bool: True if export is allowed
        """
        # Kill switch blocks everything except emergency
        if self.master_kill_switch:
            if data_type:
                full_path = f"{module}.{data_type}"
                if full_path in self.emergency_bypass:
                    return True
            return False

        # Check module settings
        if module not in self.module_settings:
            return self.new_modules_default_export

        module_config = self.module_settings[module]

        # If module config is a boolean, apply to all data types
        if isinstance(module_config, bool):
            return module_config

        # If module config is a dict, check specific data type
        if isinstance(module_config, dict):
            if data_type is None:
                # Check if any data type is allowed
                return any(module_config.values())
            return module_config.get(data_type, self.new_modules_default_export)

        return self.new_modules_default_export

    def set_module_permission(self, module, data_type=None, allowed=True):
        """Set export permission for a module or data type"""
        if module not in self.module_settings:
            self.module_settings[module] = {}

        if data_type:
            if not isinstance(self.module_settings[module], dict):
                self.module_settings[module] = {}
            self.module_settings[module][data_type] = allowed
        else:
            self.module_settings[module] = allowed

        self.save(update_fields=['module_settings', 'updated_at'])

    def enable_kill_switch(self):
        """Enable master kill switch"""
        self.master_kill_switch = True
        self.save(update_fields=['master_kill_switch', 'updated_at'])

    def disable_kill_switch(self):
        """Disable master kill switch"""
        self.master_kill_switch = False
        self.save(update_fields=['master_kill_switch', 'updated_at'])

    @classmethod
    def get_for_node(cls, node_id):
        """Get or create settings for a node"""
        obj, created = cls.objects.get_or_create(
            node_id=node_id,
            defaults={
                'module_settings': {},
                'emergency_bypass': ['birlikteyiz.earthquake_alerts']
            }
        )
        return obj


class ExportDestination(models.TextChoices):
    """Where data is being exported to"""
    HUB = 'hub', 'Hub Server'
    NODE = 'node', 'Another Node'
    EXTERNAL_API = 'external', 'External API'
    FILE = 'file', 'File Export'
    UNKNOWN = 'unknown', 'Unknown'


class ExportStatus(models.TextChoices):
    """Export operation status"""
    ALLOWED = 'allowed', 'Allowed'
    BLOCKED = 'blocked', 'Blocked'
    PENDING = 'pending', 'Pending Confirmation'
    CANCELLED = 'cancelled', 'Cancelled by User'


class DataExportLog(models.Model):
    """
    Audit log for all data export attempts.

    Logs both successful exports and blocked attempts for security monitoring.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Node identification
    node_id = models.UUIDField(db_index=True)

    # What was exported
    module = models.CharField(max_length=50, db_index=True)
    data_type = models.CharField(max_length=100, db_index=True)
    model_name = models.CharField(max_length=100, blank=True)

    # Export details
    destination_type = models.CharField(
        max_length=20,
        choices=ExportDestination.choices,
        default=ExportDestination.UNKNOWN
    )
    destination_id = models.CharField(max_length=255, blank=True)  # Node UUID or URL
    destination_name = models.CharField(max_length=255, blank=True)

    # What happened
    status = models.CharField(
        max_length=20,
        choices=ExportStatus.choices,
        default=ExportStatus.ALLOWED
    )
    blocked_reason = models.CharField(max_length=255, blank=True)

    # Data metrics
    record_count = models.IntegerField(default=0)
    size_bytes = models.BigIntegerField(default=0)

    # Request context
    request_path = models.CharField(max_length=500, blank=True)
    request_method = models.CharField(max_length=10, blank=True)
    user_id = models.UUIDField(null=True, blank=True)
    user_ip = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)

    # Timestamps
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

    # Extra data
    extra_data = models.JSONField(default=dict)

    class Meta:
        db_table = 'export_logs'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['node_id', 'timestamp']),
            models.Index(fields=['module', 'data_type']),
            models.Index(fields=['status', 'timestamp']),
        ]
        verbose_name = 'Data Export Log'
        verbose_name_plural = 'Data Export Logs'

    def __str__(self):
        return f"{self.status}: {self.module}.{self.data_type} -> {self.destination_type}"

    @classmethod
    def log_export(cls, node_id, module, data_type, destination_type,
                   status=ExportStatus.ALLOWED, **kwargs):
        """Create an export log entry"""
        return cls.objects.create(
            node_id=node_id,
            module=module,
            data_type=data_type,
            destination_type=destination_type,
            status=status,
            **kwargs
        )

    @classmethod
    def log_blocked(cls, node_id, module, data_type, destination_type, reason, **kwargs):
        """Log a blocked export attempt"""
        return cls.log_export(
            node_id=node_id,
            module=module,
            data_type=data_type,
            destination_type=destination_type,
            status=ExportStatus.BLOCKED,
            blocked_reason=reason,
            **kwargs
        )

    @classmethod
    def get_stats(cls, node_id, days=7):
        """Get export statistics for a node"""
        cutoff = timezone.now() - timedelta(days=days)
        logs = cls.objects.filter(node_id=node_id, timestamp__gte=cutoff)

        return {
            'total': logs.count(),
            'allowed': logs.filter(status=ExportStatus.ALLOWED).count(),
            'blocked': logs.filter(status=ExportStatus.BLOCKED).count(),
            'by_module': dict(
                logs.values('module').annotate(count=models.Count('id')).values_list('module', 'count')
            ),
            'by_destination': dict(
                logs.values('destination_type').annotate(count=models.Count('id')).values_list('destination_type', 'count')
            ),
            'total_records': logs.aggregate(total=models.Sum('record_count'))['total'] or 0,
            'total_bytes': logs.aggregate(total=models.Sum('size_bytes'))['total'] or 0,
        }

    @classmethod
    def cleanup_old(cls, days=90):
        """Remove old log entries"""
        cutoff = timezone.now() - timedelta(days=days)
        return cls.objects.filter(timestamp__lt=cutoff).delete()
