"""
P2P WebSocket Transport

Direct node-to-node WebSocket communication.
Supports both LAN (via router) and WiFi Direct connections.
"""

import json
import asyncio
import logging
import hashlib
import hmac
import time
import uuid
from typing import Dict, Optional, Callable, Any
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum

try:
    import websockets
    from websockets.client import WebSocketClientProtocol
    from websockets.server import WebSocketServerProtocol
    WEBSOCKETS_AVAILABLE = True
except ImportError:
    WEBSOCKETS_AVAILABLE = False

logger = logging.getLogger(__name__)


class MessageType(str, Enum):
    """P2P message types"""
    PING = "ping"
    PONG = "pong"
    DISCOVERY = "discovery"
    AUTH = "auth"
    AUTH_RESPONSE = "auth_response"
    DATA = "data"
    SYNC = "sync"
    EVENT = "event"
    ACK = "ack"
    ERROR = "error"


@dataclass
class P2PMessage:
    """P2P message structure"""
    id: str
    type: str
    from_node: str
    to_node: str
    timestamp: float
    payload: Dict[str, Any]
    signature: str = ""
    ttl: int = 3  # Time to live for relay

    def to_json(self) -> str:
        return json.dumps(asdict(self))

    @classmethod
    def from_json(cls, data: str) -> 'P2PMessage':
        return cls(**json.loads(data))

    @classmethod
    def create(cls, msg_type: MessageType, from_node: str, to_node: str,
               payload: Dict[str, Any] = None) -> 'P2PMessage':
        return cls(
            id=str(uuid.uuid4()),
            type=msg_type.value,
            from_node=from_node,
            to_node=to_node,
            timestamp=time.time(),
            payload=payload or {},
        )


class P2PConnection:
    """
    Single P2P WebSocket connection to a peer.
    """

    def __init__(self, peer_id: str, local_node_id: str, secret_key: str):
        self.peer_id = peer_id
        self.local_node_id = local_node_id
        self.secret_key = secret_key

        self.websocket: Optional[WebSocketClientProtocol] = None
        self.is_connected = False
        self.is_authenticated = False

        # Callbacks
        self.on_message: Optional[Callable[[P2PMessage], None]] = None
        self.on_disconnect: Optional[Callable[[], None]] = None

        # Stats
        self.messages_sent = 0
        self.messages_received = 0
        self.connected_at: Optional[datetime] = None
        self.last_activity: Optional[datetime] = None

    async def connect(self, address: str, port: int, timeout: float = 10.0) -> bool:
        """Connect to peer via WebSocket"""
        if not WEBSOCKETS_AVAILABLE:
            logger.error("websockets library not available")
            return False

        uri = f"ws://{address}:{port}/ws/p2p/"

        try:
            self.websocket = await asyncio.wait_for(
                websockets.connect(uri),
                timeout=timeout
            )
            self.is_connected = True
            self.connected_at = datetime.now()
            self.last_activity = datetime.now()

            logger.info(f"Connected to peer {self.peer_id} at {uri}")

            # Start authentication
            await self._authenticate()

            # Start message receiver
            asyncio.create_task(self._receive_loop())

            return True

        except asyncio.TimeoutError:
            logger.warning(f"Connection timeout to {address}:{port}")
            return False
        except Exception as e:
            logger.error(f"Connection failed to {address}:{port}: {e}")
            return False

    async def _authenticate(self):
        """Perform mutual authentication with peer"""
        # Send auth request with challenge
        challenge = str(uuid.uuid4())
        auth_msg = P2PMessage.create(
            MessageType.AUTH,
            self.local_node_id,
            self.peer_id,
            {'challenge': challenge}
        )
        auth_msg.signature = self._sign_message(auth_msg)

        await self.send(auth_msg)

    async def _receive_loop(self):
        """Receive messages from peer"""
        try:
            async for message in self.websocket:
                self.last_activity = datetime.now()
                self.messages_received += 1

                try:
                    msg = P2PMessage.from_json(message)

                    # Verify signature if present
                    if msg.signature and not self._verify_signature(msg):
                        logger.warning(f"Invalid signature from {msg.from_node}")
                        continue

                    # Handle auth response
                    if msg.type == MessageType.AUTH_RESPONSE.value:
                        self.is_authenticated = msg.payload.get('authenticated', False)
                        if self.is_authenticated:
                            logger.info(f"Authenticated with peer {self.peer_id}")
                        continue

                    # Handle ping/pong
                    if msg.type == MessageType.PING.value:
                        pong = P2PMessage.create(
                            MessageType.PONG,
                            self.local_node_id,
                            msg.from_node,
                            {'echo': msg.payload}
                        )
                        await self.send(pong)
                        continue

                    # Forward to callback
                    if self.on_message:
                        self.on_message(msg)

                except json.JSONDecodeError:
                    logger.warning("Invalid JSON message received")
                except Exception as e:
                    logger.error(f"Error processing message: {e}")

        except websockets.exceptions.ConnectionClosed:
            logger.info(f"Connection closed with {self.peer_id}")
        except Exception as e:
            logger.error(f"Receive loop error: {e}")
        finally:
            self.is_connected = False
            self.is_authenticated = False
            if self.on_disconnect:
                self.on_disconnect()

    async def send(self, message: P2PMessage) -> bool:
        """Send message to peer"""
        if not self.websocket or not self.is_connected:
            return False

        try:
            # Sign message if not already signed
            if not message.signature:
                message.signature = self._sign_message(message)

            await self.websocket.send(message.to_json())
            self.messages_sent += 1
            self.last_activity = datetime.now()
            return True

        except Exception as e:
            logger.error(f"Send failed: {e}")
            return False

    async def ping(self) -> Optional[float]:
        """Ping peer and measure latency"""
        if not self.is_connected:
            return None

        start = time.time()
        ping_id = str(uuid.uuid4())

        ping_msg = P2PMessage.create(
            MessageType.PING,
            self.local_node_id,
            self.peer_id,
            {'ping_id': ping_id, 'sent_at': start}
        )

        await self.send(ping_msg)

        # Wait for pong (simplified - real impl would use event)
        await asyncio.sleep(0.1)

        return (time.time() - start) * 1000  # ms

    async def disconnect(self):
        """Disconnect from peer"""
        if self.websocket:
            try:
                await self.websocket.close()
            except Exception:
                pass
            self.websocket = None
        self.is_connected = False
        self.is_authenticated = False

    def _sign_message(self, msg: P2PMessage) -> str:
        """Sign message with shared secret"""
        # Create signing data (exclude signature field)
        sign_data = f"{msg.id}:{msg.type}:{msg.from_node}:{msg.to_node}:{msg.timestamp}"
        signature = hmac.new(
            self.secret_key.encode(),
            sign_data.encode(),
            hashlib.sha256
        ).hexdigest()
        return signature

    def _verify_signature(self, msg: P2PMessage) -> bool:
        """Verify message signature"""
        expected = self._sign_message(msg)
        # Temporarily clear signature for verification
        original_sig = msg.signature
        msg.signature = ""
        expected = self._sign_message(msg)
        msg.signature = original_sig
        return hmac.compare_digest(expected, original_sig)


class P2PTransportService:
    """
    P2P Transport Manager.

    Manages multiple peer connections and message routing.
    """

    def __init__(self, node_id: str, secret_key: str, listen_port: int = 8001):
        self.node_id = node_id
        self.secret_key = secret_key
        self.listen_port = listen_port

        self.connections: Dict[str, P2PConnection] = {}
        self.server = None
        self._running = False

        # Callbacks
        self.on_message: Optional[Callable[[P2PMessage], None]] = None
        self.on_peer_connected: Optional[Callable[[str], None]] = None
        self.on_peer_disconnected: Optional[Callable[[str], None]] = None

    async def start_server(self):
        """Start WebSocket server for incoming connections"""
        if not WEBSOCKETS_AVAILABLE:
            logger.error("websockets library not available")
            return False

        try:
            self.server = await websockets.serve(
                self._handle_incoming,
                "0.0.0.0",
                self.listen_port
            )
            self._running = True
            logger.info(f"P2P server listening on port {self.listen_port}")
            return True

        except Exception as e:
            logger.error(f"Failed to start P2P server: {e}")
            return False

    async def _handle_incoming(self, websocket: WebSocketServerProtocol, path: str):
        """Handle incoming peer connection"""
        peer_id = None

        try:
            # Wait for auth message
            auth_data = await asyncio.wait_for(websocket.recv(), timeout=10.0)
            auth_msg = P2PMessage.from_json(auth_data)

            if auth_msg.type != MessageType.AUTH.value:
                await websocket.close(1002, "Expected AUTH message")
                return

            peer_id = auth_msg.from_node
            logger.info(f"Incoming connection from {peer_id}")

            # Verify signature
            conn = P2PConnection(peer_id, self.node_id, self.secret_key)
            if auth_msg.signature and not conn._verify_signature(auth_msg):
                await websocket.close(1002, "Invalid signature")
                return

            # Send auth response
            response = P2PMessage.create(
                MessageType.AUTH_RESPONSE,
                self.node_id,
                peer_id,
                {'authenticated': True, 'challenge_response': auth_msg.payload.get('challenge')}
            )
            response.signature = conn._sign_message(response)
            await websocket.send(response.to_json())

            # Store connection
            conn.websocket = websocket
            conn.is_connected = True
            conn.is_authenticated = True
            conn.connected_at = datetime.now()
            conn.on_message = self._handle_message
            self.connections[peer_id] = conn

            if self.on_peer_connected:
                self.on_peer_connected(peer_id)

            # Handle messages
            async for message in websocket:
                try:
                    msg = P2PMessage.from_json(message)
                    conn.messages_received += 1
                    conn.last_activity = datetime.now()

                    # Handle ping
                    if msg.type == MessageType.PING.value:
                        pong = P2PMessage.create(
                            MessageType.PONG,
                            self.node_id,
                            peer_id,
                            {'echo': msg.payload}
                        )
                        pong.signature = conn._sign_message(pong)
                        await websocket.send(pong.to_json())
                        continue

                    # Forward to handler
                    self._handle_message(msg)

                except Exception as e:
                    logger.error(f"Error processing message: {e}")

        except asyncio.TimeoutError:
            logger.warning("Auth timeout for incoming connection")
        except Exception as e:
            logger.error(f"Incoming connection error: {e}")
        finally:
            if peer_id and peer_id in self.connections:
                del self.connections[peer_id]
                if self.on_peer_disconnected:
                    self.on_peer_disconnected(peer_id)

    def _handle_message(self, msg: P2PMessage):
        """Handle received message"""
        if self.on_message:
            self.on_message(msg)

    async def connect_to_peer(self, peer_id: str, address: str, port: int) -> bool:
        """Connect to a peer"""
        if peer_id in self.connections and self.connections[peer_id].is_connected:
            return True

        conn = P2PConnection(peer_id, self.node_id, self.secret_key)
        conn.on_message = self._handle_message
        conn.on_disconnect = lambda: self._on_peer_disconnect(peer_id)

        if await conn.connect(address, port):
            self.connections[peer_id] = conn
            if self.on_peer_connected:
                self.on_peer_connected(peer_id)
            return True

        return False

    def _on_peer_disconnect(self, peer_id: str):
        """Handle peer disconnect"""
        if peer_id in self.connections:
            del self.connections[peer_id]
        if self.on_peer_disconnected:
            self.on_peer_disconnected(peer_id)

    async def send_to_peer(self, peer_id: str, msg_type: MessageType,
                           payload: Dict[str, Any]) -> bool:
        """Send message to specific peer"""
        if peer_id not in self.connections:
            return False

        conn = self.connections[peer_id]
        if not conn.is_connected:
            return False

        msg = P2PMessage.create(msg_type, self.node_id, peer_id, payload)
        return await conn.send(msg)

    async def broadcast(self, msg_type: MessageType, payload: Dict[str, Any],
                        exclude: Optional[str] = None):
        """Broadcast message to all connected peers"""
        tasks = []
        for peer_id, conn in self.connections.items():
            if peer_id != exclude and conn.is_connected:
                msg = P2PMessage.create(msg_type, self.node_id, peer_id, payload)
                tasks.append(conn.send(msg))

        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    def get_connected_peers(self) -> Dict[str, Dict]:
        """Get info about connected peers"""
        peers = {}
        for peer_id, conn in self.connections.items():
            peers[peer_id] = {
                'is_connected': conn.is_connected,
                'is_authenticated': conn.is_authenticated,
                'connected_at': conn.connected_at.isoformat() if conn.connected_at else None,
                'messages_sent': conn.messages_sent,
                'messages_received': conn.messages_received,
            }
        return peers

    async def stop(self):
        """Stop transport service"""
        # Disconnect all peers
        for conn in self.connections.values():
            await conn.disconnect()
        self.connections.clear()

        # Stop server
        if self.server:
            self.server.close()
            await self.server.wait_closed()
            self.server = None

        self._running = False
        logger.info("P2P transport service stopped")


# Singleton
_transport_service: Optional[P2PTransportService] = None


def get_transport_service() -> Optional[P2PTransportService]:
    """Get global transport service"""
    return _transport_service


def init_transport_service(node_id: str, secret_key: str,
                           listen_port: int = 8001) -> P2PTransportService:
    """Initialize global transport service"""
    global _transport_service

    if _transport_service is None:
        _transport_service = P2PTransportService(node_id, secret_key, listen_port)

    return _transport_service
