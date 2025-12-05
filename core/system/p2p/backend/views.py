"""
P2P API Views

Provides endpoints for peer discovery, connection, and messaging.
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from django.conf import settings

from .models import Peer, P2PMessage, P2PConnection, PeerStatus
from .serializers import (
    PeerSerializer,
    PeerDiscoverSerializer,
    P2PMessageSerializer,
    SendMessageSerializer,
    P2PConnectionSerializer,
    P2PStatusSerializer,
    ConnectPeerSerializer,
)
from .manager import get_p2p_manager, init_p2p_manager


class PeerViewSet(viewsets.ModelViewSet):
    """
    Peer management API.
    """
    queryset = Peer.objects.all()
    serializer_class = PeerSerializer
    permission_classes = [AllowAny]  # P2P should work without auth
    lookup_field = 'node_id'

    @action(detail=False, methods=['get'])
    def discovered(self, request):
        """
        Get discovered peers from mDNS.

        GET /api/v1/p2p/peers/discovered/
        """
        manager = get_p2p_manager()
        if not manager:
            return Response({'error': 'P2P not initialized'}, status=503)

        peers = manager.get_peers()
        data = [{
            'node_id': str(p.node_id),
            'hostname': p.hostname,
            'addresses': p.addresses,
            'version': p.version,
            'platform': p.platform,
            'connection_path': p.connection_path.value,
            'is_connected': p.is_connected,
            'latency_ms': p.latency_ms,
            'last_seen': p.last_seen.isoformat(),
            'discovered_via': p.discovered_via,
        } for p in peers]

        return Response(data)

    @action(detail=False, methods=['get'])
    def connected(self, request):
        """
        Get currently connected peers.

        GET /api/v1/p2p/peers/connected/
        """
        manager = get_p2p_manager()
        if not manager:
            return Response({'error': 'P2P not initialized'}, status=503)

        peers = manager.get_connected_peers()
        data = [{
            'node_id': str(p.node_id),
            'hostname': p.hostname,
            'latency_ms': p.latency_ms,
            'is_connected': p.is_connected,
        } for p in peers]

        return Response(data)

    @action(detail=True, methods=['post'])
    def connect(self, request, node_id=None):
        """
        Connect to a peer.

        POST /api/v1/p2p/peers/{node_id}/connect/
        """
        manager = get_p2p_manager()
        if not manager:
            return Response({'error': 'P2P not initialized'}, status=503)

        if manager.connect_to_peer(node_id):
            return Response({'status': 'connecting', 'peer_id': node_id})
        else:
            return Response(
                {'error': 'Peer not found or unreachable'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['post'])
    def ping(self, request, node_id=None):
        """
        Ping a peer.

        POST /api/v1/p2p/peers/{node_id}/ping/
        """
        manager = get_p2p_manager()
        if not manager:
            return Response({'error': 'P2P not initialized'}, status=503)

        from .transport import MessageType

        result = manager.send_message_sync(
            node_id,
            MessageType.PING,
            {'from': manager.hostname}
        )

        if result:
            return Response({'status': 'sent', 'peer_id': node_id})
        else:
            return Response(
                {'error': 'Failed to send ping'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class P2PStatusView(APIView):
    """
    P2P service status.
    """
    permission_classes = [AllowAny]

    def get(self, request):
        """
        Get P2P service status.

        GET /api/v1/p2p/status/
        """
        manager = get_p2p_manager()

        if not manager:
            return Response({
                'node_id': getattr(settings, 'NODE_UUID', 'unknown'),
                'hostname': 'unknown',
                'is_running': False,
                'discovery_enabled': False,
                'transport_enabled': False,
                'discovered_peers': 0,
                'connected_peers': 0,
                'peers': [],
            })

        peers = manager.get_peers()
        connected = manager.get_connected_peers()

        return Response({
            'node_id': manager.node_id,
            'hostname': manager.hostname,
            'is_running': manager._running,
            'discovery_enabled': manager.discovery is not None and manager.discovery.is_running(),
            'transport_enabled': manager.transport is not None,
            'discovered_peers': len(peers),
            'connected_peers': len(connected),
            'peers': [{
                'node_id': str(p.node_id),
                'hostname': p.hostname,
                'is_connected': p.is_connected,
                'latency_ms': p.latency_ms,
                'discovered_via': p.discovered_via,
            } for p in peers],
        })


class P2PStartView(APIView):
    """
    Start P2P service.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        """
        Start P2P service.

        POST /api/v1/p2p/start/
        """
        node_id = getattr(settings, 'NODE_UUID', None)
        if not node_id:
            return Response(
                {'error': 'NODE_UUID not configured'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        import socket
        hostname = socket.gethostname()
        secret_key = getattr(settings, 'SECRET_KEY', 'default-secret')
        version = getattr(settings, 'UNIBOS_VERSION', '2.0.2')
        platform = getattr(settings, 'PLATFORM_TYPE', 'unknown')

        manager = init_p2p_manager(
            node_id=str(node_id),
            hostname=hostname,
            secret_key=secret_key,
            version=version,
            platform=platform
        )
        manager.start()

        return Response({
            'status': 'started',
            'node_id': str(node_id),
            'hostname': hostname,
        })


class P2PStopView(APIView):
    """
    Stop P2P service.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        """
        Stop P2P service.

        POST /api/v1/p2p/stop/
        """
        manager = get_p2p_manager()
        if manager:
            manager.stop()
            return Response({'status': 'stopped'})
        else:
            return Response({'status': 'not_running'})


class SendMessageView(APIView):
    """
    Send P2P message.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        """
        Send message to peer.

        POST /api/v1/p2p/send/
        {
            "to_node": "uuid",
            "message_type": "data",
            "payload": {...}
        }
        """
        serializer = SendMessageSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        manager = get_p2p_manager()
        if not manager:
            return Response({'error': 'P2P not initialized'}, status=503)

        from .transport import MessageType

        data = serializer.validated_data
        msg_type = MessageType(data['message_type'])

        result = manager.send_message_sync(
            str(data['to_node']),
            msg_type,
            data.get('payload', {})
        )

        if result:
            return Response({'status': 'sent'})
        else:
            return Response(
                {'error': 'Failed to send message'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class BroadcastView(APIView):
    """
    Broadcast message to all peers.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        """
        Broadcast message.

        POST /api/v1/p2p/broadcast/
        {
            "message_type": "event",
            "payload": {...}
        }
        """
        manager = get_p2p_manager()
        if not manager:
            return Response({'error': 'P2P not initialized'}, status=503)

        from .transport import MessageType
        import asyncio

        msg_type = request.data.get('message_type', 'event')
        payload = request.data.get('payload', {})

        try:
            asyncio.run_coroutine_threadsafe(
                manager.broadcast_message(MessageType(msg_type), payload),
                manager._loop
            ).result(timeout=5.0)
            return Response({'status': 'broadcast_sent'})
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class RelayView(APIView):
    """
    Hub relay for P2P messages.
    Used when direct connection is not available.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        """
        Relay message via Hub.

        POST /api/v1/p2p/relay/
        {
            "to_node": "uuid",
            "message": "json_string"
        }
        """
        to_node = request.data.get('to_node')
        message = request.data.get('message')

        if not to_node or not message:
            return Response(
                {'error': 'to_node and message required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Store for later delivery
        # In production, this would use WebSocket to push to target node
        # For now, just log and return success
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Relay message to {to_node}")

        return Response({'status': 'relayed'})
