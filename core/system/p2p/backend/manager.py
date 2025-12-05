"""
P2P Manager

Coordinates discovery, transport, and routing for P2P communication.
Supports dual-path: Hub relay + Direct P2P connections.
"""

import asyncio
import logging
import threading
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from django.conf import settings

from .discovery import (
    P2PDiscoveryService,
    DiscoveredNode,
    init_discovery_service,
    get_discovery_service
)
from .transport import (
    P2PTransportService,
    P2PMessage,
    MessageType,
    init_transport_service,
    get_transport_service
)

logger = logging.getLogger(__name__)


class ConnectionPath(str, Enum):
    """How to reach a peer"""
    DIRECT = "direct"       # Direct WebSocket connection
    HUB = "hub"             # Via Hub relay
    BOTH = "both"           # Both paths available
    NONE = "none"           # Not reachable


@dataclass
class PeerInfo:
    """Complete peer information"""
    node_id: str
    hostname: str
    addresses: List[Dict[str, Any]]
    version: str
    platform: str
    connection_path: ConnectionPath
    is_connected: bool
    latency_ms: Optional[int]
    last_seen: datetime
    discovered_via: str  # 'mdns', 'hub', 'manual'


class P2PManager:
    """
    Main P2P coordination manager.

    Features:
    - Automatic peer discovery via mDNS
    - Direct P2P WebSocket connections
    - Hub relay fallback
    - Message routing (direct or via hub)
    - Connection health monitoring
    """

    def __init__(self, node_id: str, hostname: str, secret_key: str,
                 api_port: int = 8000, p2p_port: int = 8001,
                 version: str = "", platform: str = ""):
        self.node_id = node_id
        self.hostname = hostname
        self.secret_key = secret_key
        self.api_port = api_port
        self.p2p_port = p2p_port
        self.version = version
        self.platform = platform

        # Services
        self.discovery: Optional[P2PDiscoveryService] = None
        self.transport: Optional[P2PTransportService] = None

        # Peer registry (merged from discovery + hub)
        self.peers: Dict[str, PeerInfo] = {}
        self._peers_lock = threading.Lock()

        # Event loop for async operations
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._thread: Optional[threading.Thread] = None
        self._running = False

        # Callbacks
        self.on_peer_discovered: Optional[Callable[[PeerInfo], None]] = None
        self.on_peer_connected: Optional[Callable[[str], None]] = None
        self.on_peer_disconnected: Optional[Callable[[str], None]] = None
        self.on_message: Optional[Callable[[P2PMessage], None]] = None

        # Hub connection for relay
        self.hub_url = getattr(settings, 'UNIBOS_HUB_URL', 'https://recaria.org')

    def start(self):
        """Start P2P manager in background thread"""
        if self._running:
            return

        self._running = True

        # Initialize discovery synchronously (before async loop)
        try:
            self.discovery = init_discovery_service(
                node_id=self.node_id,
                hostname=self.hostname,
                port=self.api_port,
                version=self.version,
                platform=self.platform
            )
            self.discovery.on_peer_discovered = self._on_peer_discovered
            self.discovery.on_peer_removed = self._on_peer_removed
            discovery_started = self.discovery.start()
            if discovery_started:
                logger.info("P2P Discovery service started successfully")
            else:
                logger.warning("P2P Discovery service failed to start")
        except Exception as e:
            logger.error(f"Failed to initialize discovery: {e}", exc_info=True)

        # Start async event loop in background thread for transport
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()
        logger.info("P2P Manager started")

    def _run_loop(self):
        """Run async event loop in background thread"""
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)

        try:
            self._loop.run_until_complete(self._async_start())
            self._loop.run_forever()
        except Exception as e:
            logger.error(f"P2P event loop error: {e}", exc_info=True)
        finally:
            self._loop.close()

    async def _async_start(self):
        """Async initialization for transport"""
        # Initialize transport
        try:
            self.transport = init_transport_service(
                node_id=self.node_id,
                secret_key=self.secret_key,
                listen_port=self.p2p_port
            )
            self.transport.on_peer_connected = self._on_transport_connected
            self.transport.on_peer_disconnected = self._on_transport_disconnected
            self.transport.on_message = self._on_transport_message
            await self.transport.start_server()
            logger.info(f"P2P Transport server started on port {self.p2p_port}")
        except Exception as e:
            logger.error(f"Failed to initialize transport: {e}", exc_info=True)

        # Start periodic tasks
        asyncio.create_task(self._health_check_loop())
        asyncio.create_task(self._hub_sync_loop())

    def stop(self):
        """Stop P2P manager"""
        if not self._running:
            return

        self._running = False

        if self.discovery:
            self.discovery.stop()

        if self._loop:
            if self.transport:
                asyncio.run_coroutine_threadsafe(
                    self.transport.stop(),
                    self._loop
                )
            self._loop.call_soon_threadsafe(self._loop.stop)

        if self._thread:
            self._thread.join(timeout=5.0)

        logger.info("P2P Manager stopped")

    def _on_peer_discovered(self, node: DiscoveredNode):
        """Handle mDNS peer discovery"""
        with self._peers_lock:
            peer_info = PeerInfo(
                node_id=node.node_id,
                hostname=node.hostname,
                addresses=node.addresses,
                version=node.version,
                platform=node.platform,
                connection_path=ConnectionPath.DIRECT,  # mDNS = direct possible
                is_connected=False,
                latency_ms=None,
                last_seen=node.last_seen,
                discovered_via='mdns'
            )

            # Update or add peer
            existing = self.peers.get(node.node_id)
            if existing:
                # Merge addresses
                existing_ips = {a.get('ip') for a in existing.addresses}
                for addr in node.addresses:
                    if addr.get('ip') not in existing_ips:
                        existing.addresses.append(addr)
                existing.last_seen = node.last_seen
                if existing.connection_path == ConnectionPath.HUB:
                    existing.connection_path = ConnectionPath.BOTH
            else:
                self.peers[node.node_id] = peer_info

        logger.info(f"Peer discovered via mDNS: {node.hostname}")

        # Auto-connect if enabled
        if getattr(settings, 'P2P_AUTO_CONNECT', True):
            self._schedule_connect(node.node_id)

        if self.on_peer_discovered:
            self.on_peer_discovered(peer_info)

    def _on_peer_removed(self, name: str):
        """Handle mDNS peer removal"""
        # Note: We don't remove from peers, just update connection path
        pass

    def _on_transport_connected(self, peer_id: str):
        """Handle transport connection"""
        with self._peers_lock:
            if peer_id in self.peers:
                self.peers[peer_id].is_connected = True

        if self.on_peer_connected:
            self.on_peer_connected(peer_id)

    def _on_transport_disconnected(self, peer_id: str):
        """Handle transport disconnection"""
        with self._peers_lock:
            if peer_id in self.peers:
                self.peers[peer_id].is_connected = False

        if self.on_peer_disconnected:
            self.on_peer_disconnected(peer_id)

    def _on_transport_message(self, msg: P2PMessage):
        """Handle incoming P2P message"""
        logger.debug(f"P2P message from {msg.from_node}: {msg.type}")

        if self.on_message:
            self.on_message(msg)

    def _schedule_connect(self, peer_id: str):
        """Schedule connection to peer"""
        if self._loop:
            asyncio.run_coroutine_threadsafe(
                self._connect_to_peer(peer_id),
                self._loop
            )

    async def _connect_to_peer(self, peer_id: str):
        """Attempt to connect to peer"""
        with self._peers_lock:
            peer = self.peers.get(peer_id)
            if not peer or peer.is_connected:
                return

        # Try each address
        for addr in peer.addresses:
            ip = addr.get('ip')
            port = addr.get('port', self.p2p_port)

            if ip and await self.transport.connect_to_peer(peer_id, ip, port):
                logger.info(f"Connected to {peer.hostname} at {ip}:{port}")
                return

        logger.warning(f"Could not connect to {peer.hostname}")

    async def _health_check_loop(self):
        """Periodic health check for connections"""
        while self._running:
            try:
                await asyncio.sleep(60)  # Check every minute

                for peer_id, conn in list(self.transport.connections.items()):
                    if conn.is_connected:
                        latency = await conn.ping()
                        with self._peers_lock:
                            if peer_id in self.peers:
                                self.peers[peer_id].latency_ms = int(latency) if latency else None

            except Exception as e:
                logger.error(f"Health check error: {e}")

    async def _hub_sync_loop(self):
        """Sync peer list with Hub periodically"""
        while self._running:
            try:
                await asyncio.sleep(300)  # Sync every 5 minutes
                await self._sync_with_hub()

            except Exception as e:
                logger.error(f"Hub sync error: {e}")

    async def _sync_with_hub(self):
        """Fetch peer list from Hub"""
        import aiohttp

        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.hub_url}/api/v1/nodes/discover/"
                async with session.get(url, timeout=10) as resp:
                    if resp.status == 200:
                        nodes = await resp.json()
                        self._update_peers_from_hub(nodes)

        except Exception as e:
            logger.debug(f"Hub sync failed: {e}")

    def _update_peers_from_hub(self, nodes: List[Dict]):
        """Update peer registry from Hub data"""
        with self._peers_lock:
            for node in nodes:
                node_id = node.get('id')
                if not node_id or node_id == self.node_id:
                    continue

                if node_id in self.peers:
                    # Update existing
                    peer = self.peers[node_id]
                    if peer.connection_path == ConnectionPath.DIRECT:
                        peer.connection_path = ConnectionPath.BOTH
                else:
                    # New peer from hub
                    addresses = []
                    if node.get('ip_address'):
                        addresses.append({
                            'ip': node['ip_address'],
                            'port': node.get('port', 8000)
                        })

                    self.peers[node_id] = PeerInfo(
                        node_id=node_id,
                        hostname=node.get('hostname', 'unknown'),
                        addresses=addresses,
                        version=node.get('version', ''),
                        platform=node.get('platform', ''),
                        connection_path=ConnectionPath.HUB,
                        is_connected=False,
                        latency_ms=None,
                        last_seen=datetime.now(),
                        discovered_via='hub'
                    )

    # Public API

    def get_peers(self) -> List[PeerInfo]:
        """Get list of known peers"""
        with self._peers_lock:
            return list(self.peers.values())

    def get_peer(self, peer_id: str) -> Optional[PeerInfo]:
        """Get specific peer info"""
        with self._peers_lock:
            return self.peers.get(peer_id)

    def get_connected_peers(self) -> List[PeerInfo]:
        """Get list of connected peers"""
        with self._peers_lock:
            return [p for p in self.peers.values() if p.is_connected]

    async def send_message(self, peer_id: str, msg_type: MessageType,
                           payload: Dict[str, Any]) -> bool:
        """Send message to peer (direct or via hub)"""
        with self._peers_lock:
            peer = self.peers.get(peer_id)
            if not peer:
                return False

        # Try direct if connected
        if peer.is_connected and self.transport:
            return await self.transport.send_to_peer(peer_id, msg_type, payload)

        # Fallback to hub relay
        if peer.connection_path in [ConnectionPath.HUB, ConnectionPath.BOTH]:
            return await self._send_via_hub(peer_id, msg_type, payload)

        return False

    async def _send_via_hub(self, peer_id: str, msg_type: MessageType,
                            payload: Dict[str, Any]) -> bool:
        """Send message via Hub relay"""
        import aiohttp

        try:
            msg = P2PMessage.create(msg_type, self.node_id, peer_id, payload)

            async with aiohttp.ClientSession() as session:
                url = f"{self.hub_url}/api/v1/p2p/relay/"
                async with session.post(url, json={
                    'to_node': peer_id,
                    'message': msg.to_json()
                }, timeout=10) as resp:
                    return resp.status == 200

        except Exception as e:
            logger.error(f"Hub relay failed: {e}")
            return False

    def send_message_sync(self, peer_id: str, msg_type: MessageType,
                          payload: Dict[str, Any]) -> bool:
        """Synchronous wrapper for send_message"""
        if not self._loop:
            return False

        future = asyncio.run_coroutine_threadsafe(
            self.send_message(peer_id, msg_type, payload),
            self._loop
        )
        try:
            return future.result(timeout=10.0)
        except Exception:
            return False

    async def broadcast_message(self, msg_type: MessageType,
                                payload: Dict[str, Any]):
        """Broadcast message to all peers"""
        if self.transport:
            await self.transport.broadcast(msg_type, payload)

    def connect_to_peer(self, peer_id: str) -> bool:
        """Request connection to peer"""
        if peer_id not in self.peers:
            return False

        self._schedule_connect(peer_id)
        return True


# Singleton
_p2p_manager: Optional[P2PManager] = None


def get_p2p_manager() -> Optional[P2PManager]:
    """Get global P2P manager"""
    return _p2p_manager


def init_p2p_manager(node_id: str, hostname: str, secret_key: str,
                     **kwargs) -> P2PManager:
    """Initialize global P2P manager"""
    global _p2p_manager

    if _p2p_manager is None:
        _p2p_manager = P2PManager(
            node_id=node_id,
            hostname=hostname,
            secret_key=secret_key,
            **kwargs
        )

    return _p2p_manager
