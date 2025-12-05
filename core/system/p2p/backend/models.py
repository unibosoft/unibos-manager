"""
P2P Communication Models

Models for peer discovery, connections, and message tracking.
"""

import uuid
from django.db import models
from django.utils import timezone


class PeerStatus(models.TextChoices):
    """Peer connection status"""
    DISCOVERED = 'discovered', 'Discovered'
    CONNECTING = 'connecting', 'Connecting'
    CONNECTED = 'connected', 'Connected'
    DISCONNECTED = 'disconnected', 'Disconnected'
    UNREACHABLE = 'unreachable', 'Unreachable'
    BLOCKED = 'blocked', 'Blocked'


class DiscoveryMethod(models.TextChoices):
    """How the peer was discovered"""
    MDNS = 'mdns', 'mDNS (Local Network)'
    HUB = 'hub', 'Hub Registry'
    MANUAL = 'manual', 'Manual Entry'
    BROADCAST = 'broadcast', 'Network Broadcast'


class MessageType(models.TextChoices):
    """P2P message types"""
    PING = 'ping', 'Ping'
    PONG = 'pong', 'Pong'
    DISCOVERY = 'discovery', 'Discovery'
    AUTH = 'auth', 'Authentication'
    DATA = 'data', 'Data Transfer'
    SYNC = 'sync', 'Sync Request'
    EVENT = 'event', 'Real-time Event'
    ACK = 'ack', 'Acknowledgment'


class Peer(models.Model):
    """
    Discovered peer node in the P2P network.

    Tracks nodes discovered via mDNS or Hub registry.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Peer identification
    node_id = models.UUIDField(db_index=True, unique=True)
    hostname = models.CharField(max_length=255)

    # Network addresses (multiple interfaces possible)
    addresses = models.JSONField(default=list)  # [{"ip": "192.168.0.140", "port": 8000, "interface": "eth0"}]
    primary_address = models.GenericIPAddressField(null=True, blank=True)
    primary_port = models.PositiveIntegerField(default=8000)

    # Connection info
    status = models.CharField(
        max_length=20,
        choices=PeerStatus.choices,
        default=PeerStatus.DISCOVERED
    )
    discovery_method = models.CharField(
        max_length=20,
        choices=DiscoveryMethod.choices,
        default=DiscoveryMethod.MDNS
    )

    # Peer metadata from mDNS TXT records
    version = models.CharField(max_length=50, blank=True)
    platform = models.CharField(max_length=50, blank=True)
    capabilities = models.JSONField(default=dict)

    # Trust & Security
    is_trusted = models.BooleanField(default=False)
    trust_level = models.IntegerField(default=1)  # 1=unknown, 2=known, 3=trusted, 4=verified, 5=owner
    public_key = models.TextField(blank=True)  # For message verification

    # Connection metrics
    last_seen = models.DateTimeField(auto_now=True)
    last_connected = models.DateTimeField(null=True, blank=True)
    connection_failures = models.IntegerField(default=0)
    latency_ms = models.IntegerField(null=True, blank=True)

    # Discovery timestamps
    first_discovered = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'p2p_peers'
        verbose_name = 'Peer'
        verbose_name_plural = 'Peers'
        ordering = ['-last_seen']
        indexes = [
            models.Index(fields=['status', 'last_seen']),
            models.Index(fields=['discovery_method']),
        ]

    def __str__(self):
        return f"{self.hostname} ({self.primary_address})"

    def update_seen(self):
        """Update last seen timestamp"""
        self.last_seen = timezone.now()
        self.save(update_fields=['last_seen'])

    def mark_connected(self, latency_ms=None):
        """Mark peer as connected"""
        self.status = PeerStatus.CONNECTED
        self.last_connected = timezone.now()
        self.connection_failures = 0
        if latency_ms:
            self.latency_ms = latency_ms
        self.save(update_fields=['status', 'last_connected', 'connection_failures', 'latency_ms'])

    def mark_disconnected(self):
        """Mark peer as disconnected"""
        self.status = PeerStatus.DISCONNECTED
        self.save(update_fields=['status'])

    def mark_failed(self):
        """Record connection failure"""
        self.connection_failures += 1
        if self.connection_failures >= 3:
            self.status = PeerStatus.UNREACHABLE
        self.save(update_fields=['connection_failures', 'status'])

    def get_best_address(self):
        """Get best address for connection (prefer same subnet)"""
        if self.primary_address:
            return (self.primary_address, self.primary_port)
        if self.addresses:
            # Return first available
            addr = self.addresses[0]
            return (addr.get('ip'), addr.get('port', 8000))
        return None


class P2PMessage(models.Model):
    """
    P2P message log for auditing and debugging.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Message routing
    from_node = models.UUIDField(db_index=True)
    to_node = models.UUIDField(db_index=True)

    # Message content
    message_type = models.CharField(
        max_length=20,
        choices=MessageType.choices,
        default=MessageType.DATA
    )
    payload = models.JSONField(default=dict)

    # Routing info
    via_hub = models.BooleanField(default=False)  # True if relayed through Hub
    direct = models.BooleanField(default=False)   # True if sent directly

    # Status
    sent_at = models.DateTimeField(auto_now_add=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    acknowledged_at = models.DateTimeField(null=True, blank=True)

    # Security
    signature = models.TextField(blank=True)
    verified = models.BooleanField(default=False)

    class Meta:
        db_table = 'p2p_messages'
        verbose_name = 'P2P Message'
        verbose_name_plural = 'P2P Messages'
        ordering = ['-sent_at']
        indexes = [
            models.Index(fields=['from_node', 'sent_at']),
            models.Index(fields=['to_node', 'sent_at']),
            models.Index(fields=['message_type']),
        ]

    def __str__(self):
        return f"{self.message_type}: {self.from_node} -> {self.to_node}"


class P2PConnection(models.Model):
    """
    Active P2P connection tracking.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    peer = models.ForeignKey(Peer, on_delete=models.CASCADE, related_name='connections')

    # Connection details
    local_address = models.GenericIPAddressField()
    local_port = models.PositiveIntegerField()
    remote_address = models.GenericIPAddressField()
    remote_port = models.PositiveIntegerField()

    # Connection type
    is_websocket = models.BooleanField(default=True)
    is_incoming = models.BooleanField(default=False)

    # Status
    connected_at = models.DateTimeField(auto_now_add=True)
    disconnected_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    # Stats
    messages_sent = models.IntegerField(default=0)
    messages_received = models.IntegerField(default=0)
    bytes_sent = models.BigIntegerField(default=0)
    bytes_received = models.BigIntegerField(default=0)

    class Meta:
        db_table = 'p2p_connections'
        verbose_name = 'P2P Connection'
        verbose_name_plural = 'P2P Connections'
        ordering = ['-connected_at']

    def __str__(self):
        direction = "<-" if self.is_incoming else "->"
        return f"{self.local_address}:{self.local_port} {direction} {self.remote_address}:{self.remote_port}"
