"""
P2P API Serializers
"""

from rest_framework import serializers
from .models import Peer, P2PMessage, P2PConnection, PeerStatus, DiscoveryMethod


class PeerSerializer(serializers.ModelSerializer):
    """Serializer for Peer model"""
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    discovery_method_display = serializers.CharField(source='get_discovery_method_display', read_only=True)
    best_address = serializers.SerializerMethodField()

    class Meta:
        model = Peer
        fields = [
            'id', 'node_id', 'hostname',
            'addresses', 'primary_address', 'primary_port',
            'status', 'status_display',
            'discovery_method', 'discovery_method_display',
            'version', 'platform', 'capabilities',
            'is_trusted', 'trust_level',
            'last_seen', 'last_connected',
            'latency_ms', 'connection_failures',
            'first_discovered',
            'best_address',
        ]
        read_only_fields = ['id', 'first_discovered', 'last_seen']

    def get_best_address(self, obj):
        addr = obj.get_best_address()
        if addr:
            return {'ip': addr[0], 'port': addr[1]}
        return None


class PeerDiscoverSerializer(serializers.Serializer):
    """Serializer for peer discovery request"""
    node_id = serializers.UUIDField()
    hostname = serializers.CharField(max_length=255)
    addresses = serializers.ListField(
        child=serializers.DictField(),
        required=False,
        default=list
    )
    port = serializers.IntegerField(default=8000)
    version = serializers.CharField(max_length=50, required=False, default='')
    platform = serializers.CharField(max_length=50, required=False, default='')
    capabilities = serializers.DictField(required=False, default=dict)


class P2PMessageSerializer(serializers.ModelSerializer):
    """Serializer for P2P messages"""
    type_display = serializers.CharField(source='get_message_type_display', read_only=True)

    class Meta:
        model = P2PMessage
        fields = [
            'id', 'from_node', 'to_node',
            'message_type', 'type_display',
            'payload', 'via_hub', 'direct',
            'sent_at', 'delivered_at', 'acknowledged_at',
            'signature', 'verified',
        ]
        read_only_fields = ['id', 'sent_at']


class SendMessageSerializer(serializers.Serializer):
    """Serializer for sending P2P message"""
    to_node = serializers.UUIDField()
    message_type = serializers.ChoiceField(choices=[
        ('ping', 'Ping'),
        ('data', 'Data'),
        ('sync', 'Sync'),
        ('event', 'Event'),
    ])
    payload = serializers.DictField(required=False, default=dict)


class P2PConnectionSerializer(serializers.ModelSerializer):
    """Serializer for P2P connections"""
    peer_hostname = serializers.CharField(source='peer.hostname', read_only=True)

    class Meta:
        model = P2PConnection
        fields = [
            'id', 'peer', 'peer_hostname',
            'local_address', 'local_port',
            'remote_address', 'remote_port',
            'is_websocket', 'is_incoming',
            'connected_at', 'disconnected_at', 'is_active',
            'messages_sent', 'messages_received',
            'bytes_sent', 'bytes_received',
        ]
        read_only_fields = ['id', 'connected_at']


class P2PStatusSerializer(serializers.Serializer):
    """Serializer for P2P status response"""
    node_id = serializers.CharField()
    hostname = serializers.CharField()
    is_running = serializers.BooleanField()
    discovery_enabled = serializers.BooleanField()
    transport_enabled = serializers.BooleanField()
    discovered_peers = serializers.IntegerField()
    connected_peers = serializers.IntegerField()
    peers = PeerSerializer(many=True)


class ConnectPeerSerializer(serializers.Serializer):
    """Serializer for connect to peer request"""
    peer_id = serializers.UUIDField(required=False)
    address = serializers.IPAddressField(required=False)
    port = serializers.IntegerField(default=8001)

    def validate(self, data):
        if not data.get('peer_id') and not data.get('address'):
            raise serializers.ValidationError(
                "Either peer_id or address must be provided"
            )
        return data
