"""
WebSocket consumers for authentication notifications.

Provides real-time notifications for:
- Session events (login, logout, new device)
- Account link status changes
- Permission sync updates
- Security alerts
"""

import json
import logging
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from asgiref.sync import sync_to_async

logger = logging.getLogger('authentication')


class AuthNotificationConsumer(AsyncJsonWebsocketConsumer):
    """
    WebSocket consumer for authentication notifications.

    Users subscribe to their own auth events channel.
    Hub can push notifications to specific users or broadcast.
    """

    async def connect(self):
        """Handle WebSocket connection"""
        user = self.scope.get('user')

        if not user or user.is_anonymous:
            await self.close(code=4001)
            return

        self.user = user
        self.user_group = f"auth_user_{user.id}"

        # Join user's personal notification group
        await self.channel_layer.group_add(
            self.user_group,
            self.channel_name
        )

        # Join global auth notifications group (for broadcasts)
        await self.channel_layer.group_add(
            "auth_global",
            self.channel_name
        )

        await self.accept()
        logger.info(f"Auth WebSocket connected: {user.username}")

        # Send initial connection status
        await self.send_json({
            'type': 'connection_established',
            'user_id': str(user.id),
            'username': user.username,
        })

    async def disconnect(self, close_code):
        """Handle WebSocket disconnection"""
        if hasattr(self, 'user_group'):
            await self.channel_layer.group_discard(
                self.user_group,
                self.channel_name
            )

        await self.channel_layer.group_discard(
            "auth_global",
            self.channel_name
        )

        if hasattr(self, 'user'):
            logger.info(f"Auth WebSocket disconnected: {self.user.username}")

    async def receive_json(self, content):
        """Handle incoming WebSocket messages"""
        message_type = content.get('type')

        if message_type == 'ping':
            await self.send_json({'type': 'pong'})

        elif message_type == 'subscribe_link_status':
            # Subscribe to account link status updates
            await self.send_json({
                'type': 'subscribed',
                'channel': 'link_status'
            })

        elif message_type == 'get_sessions':
            # Get active sessions
            sessions = await self.get_active_sessions()
            await self.send_json({
                'type': 'sessions_list',
                'sessions': sessions
            })

    # ========== Channel Layer Handlers ==========

    async def auth_session_created(self, event):
        """New session created notification"""
        await self.send_json({
            'type': 'session_created',
            'session': event.get('session'),
            'device_info': event.get('device_info'),
            'ip_address': event.get('ip_address'),
            'timestamp': event.get('timestamp'),
        })

    async def auth_session_revoked(self, event):
        """Session revoked notification"""
        await self.send_json({
            'type': 'session_revoked',
            'session_id': event.get('session_id'),
            'reason': event.get('reason'),
            'timestamp': event.get('timestamp'),
        })

    async def auth_password_changed(self, event):
        """Password changed notification"""
        await self.send_json({
            'type': 'password_changed',
            'timestamp': event.get('timestamp'),
            'message': 'Your password has been changed. All other sessions have been logged out.'
        })

    async def auth_link_status_changed(self, event):
        """Account link status changed notification"""
        await self.send_json({
            'type': 'link_status_changed',
            'link_id': event.get('link_id'),
            'status': event.get('status'),
            'hub_username': event.get('hub_username'),
            'timestamp': event.get('timestamp'),
        })

    async def auth_permissions_synced(self, event):
        """Permissions synced from Hub notification"""
        await self.send_json({
            'type': 'permissions_synced',
            'permissions_count': event.get('permissions_count'),
            'roles_count': event.get('roles_count'),
            'timestamp': event.get('timestamp'),
        })

    async def auth_security_alert(self, event):
        """Security alert notification"""
        await self.send_json({
            'type': 'security_alert',
            'alert_type': event.get('alert_type'),
            'message': event.get('message'),
            'severity': event.get('severity', 'warning'),
            'timestamp': event.get('timestamp'),
        })

    async def auth_broadcast(self, event):
        """Global broadcast message"""
        await self.send_json({
            'type': 'broadcast',
            'message': event.get('message'),
            'timestamp': event.get('timestamp'),
        })

    # ========== Helper Methods ==========

    @database_sync_to_async
    def get_active_sessions(self):
        """Get user's active sessions"""
        from .models import UserSession

        sessions = UserSession.objects.filter(
            user=self.user,
            is_active=True
        ).values(
            'id', 'ip_address', 'user_agent', 'device_info',
            'created_at', 'last_activity'
        )

        return [
            {
                'id': str(s['id']),
                'ip_address': s['ip_address'],
                'user_agent': s['user_agent'],
                'device_info': s['device_info'],
                'created_at': s['created_at'].isoformat() if s['created_at'] else None,
                'last_activity': s['last_activity'].isoformat() if s['last_activity'] else None,
            }
            for s in sessions
        ]


# ========== Utility Functions for Sending Notifications ==========

async def send_auth_notification(user_id, notification_type, data):
    """
    Send authentication notification to a specific user.

    Args:
        user_id: User ID to send notification to
        notification_type: Type of notification (e.g., 'auth_session_created')
        data: Dictionary of notification data
    """
    from channels.layers import get_channel_layer

    channel_layer = get_channel_layer()
    group_name = f"auth_user_{user_id}"

    await channel_layer.group_send(group_name, {
        'type': notification_type,
        **data
    })


async def broadcast_auth_notification(notification_type, data):
    """
    Broadcast authentication notification to all connected users.

    Args:
        notification_type: Type of notification
        data: Dictionary of notification data
    """
    from channels.layers import get_channel_layer

    channel_layer = get_channel_layer()

    await channel_layer.group_send("auth_global", {
        'type': notification_type,
        **data
    })


def send_auth_notification_sync(user_id, notification_type, data):
    """
    Synchronous wrapper for send_auth_notification.
    Use this from Django views/signals.
    """
    import asyncio
    from asgiref.sync import async_to_sync
    from channels.layers import get_channel_layer

    channel_layer = get_channel_layer()
    group_name = f"auth_user_{user_id}"

    async_to_sync(channel_layer.group_send)(group_name, {
        'type': notification_type,
        **data
    })
