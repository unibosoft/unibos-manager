"""
P2P WebSocket Consumer

Handles WebSocket connections for direct P2P communication.
"""

import json
import logging
import asyncio
from typing import Optional
from channels.generic.websocket import AsyncWebsocketConsumer
from django.conf import settings

from .manager import get_p2p_manager
from .transport import MessageType

logger = logging.getLogger(__name__)


class P2PConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for P2P communication.

    Handles incoming P2P connections and messages.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.peer_id: Optional[str] = None
        self.authenticated = False

    async def connect(self):
        """Accept WebSocket connection"""
        await self.accept()
        logger.info(f"P2P WebSocket connection accepted from {self.scope.get('client', 'unknown')}")

    async def disconnect(self, close_code):
        """Handle disconnection"""
        manager = get_p2p_manager()
        if manager and self.peer_id:
            # Notify manager of disconnection
            manager._on_transport_disconnected(self.peer_id)

        logger.info(f"P2P WebSocket disconnected: {self.peer_id or 'unauthenticated'} (code: {close_code})")

    async def receive(self, text_data=None, bytes_data=None):
        """Handle incoming message"""
        if not text_data:
            return

        try:
            data = json.loads(text_data)
            msg_type = data.get('type', '')
            payload = data.get('payload', {})

            # Handle different message types
            if msg_type == MessageType.PING.value:
                await self._handle_ping(data)
            elif msg_type == MessageType.PONG.value:
                await self._handle_pong(data)
            elif msg_type == MessageType.AUTH.value:
                await self._handle_auth(data)
            elif msg_type == MessageType.DATA.value:
                await self._handle_data(data)
            elif msg_type == MessageType.SYNC.value:
                await self._handle_sync(data)
            elif msg_type == MessageType.EVENT.value:
                await self._handle_event(data)
            else:
                logger.warning(f"Unknown P2P message type: {msg_type}")

        except json.JSONDecodeError:
            logger.error(f"Invalid JSON in P2P message")
        except Exception as e:
            logger.error(f"Error handling P2P message: {e}")

    async def _handle_ping(self, data):
        """Handle ping message - respond with pong"""
        pong = {
            'id': data.get('id'),
            'type': MessageType.PONG.value,
            'from_node': getattr(settings, 'NODE_UUID', ''),
            'to_node': data.get('from_node', ''),
            'timestamp': data.get('timestamp'),
            'payload': {'status': 'ok'}
        }
        await self.send(text_data=json.dumps(pong))

    async def _handle_pong(self, data):
        """Handle pong message"""
        manager = get_p2p_manager()
        if manager and manager.transport:
            # Update latency
            manager.transport._handle_pong_response(data)

    async def _handle_auth(self, data):
        """Handle authentication message"""
        self.peer_id = data.get('from_node')
        self.authenticated = True

        manager = get_p2p_manager()
        if manager:
            manager._on_transport_connected(self.peer_id)

        # Send auth response
        response = {
            'id': data.get('id'),
            'type': MessageType.AUTH.value,
            'from_node': getattr(settings, 'NODE_UUID', ''),
            'to_node': self.peer_id,
            'payload': {
                'status': 'authenticated',
                'node_id': str(getattr(settings, 'NODE_UUID', '')),
                'hostname': getattr(settings, 'NODE_HOSTNAME', 'unknown'),
            }
        }
        await self.send(text_data=json.dumps(response))
        logger.info(f"P2P peer authenticated: {self.peer_id}")

    async def _handle_data(self, data):
        """Handle data message"""
        manager = get_p2p_manager()
        if manager and manager.on_message:
            # Forward to manager callback
            from .transport import P2PMessage
            msg = P2PMessage(
                id=data.get('id', ''),
                type=MessageType.DATA,
                from_node=data.get('from_node', ''),
                to_node=data.get('to_node', ''),
                payload=data.get('payload', {}),
            )
            manager.on_message(msg)

    async def _handle_sync(self, data):
        """Handle sync request"""
        # Forward to sync engine
        logger.info(f"P2P sync request from {data.get('from_node')}")

    async def _handle_event(self, data):
        """Handle real-time event"""
        # Forward to event handlers
        logger.info(f"P2P event from {data.get('from_node')}: {data.get('payload', {}).get('event_type')}")

    async def send_message(self, message: dict):
        """Send message to connected peer"""
        await self.send(text_data=json.dumps(message))
