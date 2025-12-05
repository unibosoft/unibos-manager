"""
Messenger WebSocket Consumers

Real-time messaging via WebSocket.
Supports both Hub relay and P2P messaging modes.
"""

import json
import logging
from typing import Optional, Dict, Any
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone

logger = logging.getLogger('messenger.websocket')


class MessengerConsumer(AsyncJsonWebsocketConsumer):
    """
    Main WebSocket consumer for messenger.

    Handles:
    - Real-time message delivery
    - Typing indicators
    - Read receipts
    - P2P signaling (offer/answer/ICE)
    - Online presence
    """

    async def connect(self):
        """Handle WebSocket connection"""
        user = self.scope.get('user')

        if not user or user.is_anonymous:
            await self.close(code=4001)
            return

        self.user = user
        self.user_id = str(user.id)
        self.user_group = f"messenger_user_{self.user_id}"
        self.conversation_groups = set()

        # Join user's personal group (for P2P signaling, DMs)
        await self.channel_layer.group_add(
            self.user_group,
            self.channel_name
        )

        # Load user's conversations and join their groups
        conversation_ids = await self.get_user_conversations()
        for conv_id in conversation_ids:
            group_name = f"messenger_conversation_{conv_id}"
            await self.channel_layer.group_add(group_name, self.channel_name)
            self.conversation_groups.add(group_name)

        await self.accept()
        logger.info(f"Messenger WebSocket connected: {user.username}")

        # Notify presence
        await self.broadcast_presence(True)

        # Send connection confirmation
        await self.send_json({
            'type': 'connection_established',
            'user_id': self.user_id,
            'conversations_joined': len(conversation_ids)
        })

    async def disconnect(self, close_code):
        """Handle WebSocket disconnection"""
        # Leave all groups
        if hasattr(self, 'user_group'):
            await self.channel_layer.group_discard(
                self.user_group,
                self.channel_name
            )

        for group_name in getattr(self, 'conversation_groups', set()):
            await self.channel_layer.group_discard(group_name, self.channel_name)

        # Notify presence (offline)
        if hasattr(self, 'user'):
            await self.broadcast_presence(False)
            logger.info(f"Messenger WebSocket disconnected: {self.user.username}")

    async def receive_json(self, content: Dict[str, Any]):
        """Handle incoming WebSocket messages"""
        message_type = content.get('type', '')

        handlers = {
            'ping': self.handle_ping,
            'join_conversation': self.handle_join_conversation,
            'leave_conversation': self.handle_leave_conversation,
            'typing.start': self.handle_typing_start,
            'typing.stop': self.handle_typing_stop,
            'message.read': self.handle_message_read,
            'p2p.offer': self.handle_p2p_offer,
            'p2p.answer': self.handle_p2p_answer,
            'p2p.ice': self.handle_p2p_ice,
            'p2p.message': self.handle_p2p_message,
        }

        handler = handlers.get(message_type)
        if handler:
            await handler(content)
        else:
            await self.send_json({
                'type': 'error',
                'message': f'Unknown message type: {message_type}'
            })

    # ========== Message Handlers ==========

    async def handle_ping(self, content):
        """Respond to ping"""
        await self.send_json({'type': 'pong', 'timestamp': timezone.now().isoformat()})

    async def handle_join_conversation(self, content):
        """Join a conversation's group"""
        conversation_id = content.get('conversation_id')

        if not await self.verify_conversation_access(conversation_id):
            await self.send_json({
                'type': 'error',
                'message': 'Access denied to conversation'
            })
            return

        group_name = f"messenger_conversation_{conversation_id}"
        if group_name not in self.conversation_groups:
            await self.channel_layer.group_add(group_name, self.channel_name)
            self.conversation_groups.add(group_name)

        await self.send_json({
            'type': 'conversation_joined',
            'conversation_id': conversation_id
        })

    async def handle_leave_conversation(self, content):
        """Leave a conversation's group"""
        conversation_id = content.get('conversation_id')
        group_name = f"messenger_conversation_{conversation_id}"

        if group_name in self.conversation_groups:
            await self.channel_layer.group_discard(group_name, self.channel_name)
            self.conversation_groups.remove(group_name)

        await self.send_json({
            'type': 'conversation_left',
            'conversation_id': conversation_id
        })

    async def handle_typing_start(self, content):
        """Broadcast typing indicator start"""
        conversation_id = content.get('conversation_id')

        if not await self.verify_conversation_access(conversation_id):
            return

        group_name = f"messenger_conversation_{conversation_id}"
        await self.channel_layer.group_send(group_name, {
            'type': 'typing.start',
            'user_id': self.user_id,
            'username': self.user.username,
            'conversation_id': conversation_id
        })

    async def handle_typing_stop(self, content):
        """Broadcast typing indicator stop"""
        conversation_id = content.get('conversation_id')

        if not await self.verify_conversation_access(conversation_id):
            return

        group_name = f"messenger_conversation_{conversation_id}"
        await self.channel_layer.group_send(group_name, {
            'type': 'typing.stop',
            'user_id': self.user_id,
            'username': self.user.username,
            'conversation_id': conversation_id
        })

    async def handle_message_read(self, content):
        """Handle message read notification"""
        conversation_id = content.get('conversation_id')
        message_id = content.get('message_id')

        if not await self.verify_conversation_access(conversation_id):
            return

        # Update database
        await self.mark_message_read(message_id)

        # Broadcast to conversation
        group_name = f"messenger_conversation_{conversation_id}"
        await self.channel_layer.group_send(group_name, {
            'type': 'message.read',
            'user_id': self.user_id,
            'username': self.user.username,
            'message_id': message_id,
            'read_at': timezone.now().isoformat()
        })

    # ========== P2P Signaling Handlers ==========

    async def handle_p2p_offer(self, content):
        """Forward P2P connection offer"""
        target_user_id = content.get('target_user_id')
        offer = content.get('offer')
        session_id = content.get('session_id')

        target_group = f"messenger_user_{target_user_id}"
        await self.channel_layer.group_send(target_group, {
            'type': 'p2p.offer',
            'from_user_id': self.user_id,
            'from_username': self.user.username,
            'session_id': session_id,
            'offer': offer
        })

    async def handle_p2p_answer(self, content):
        """Forward P2P connection answer"""
        target_user_id = content.get('target_user_id')
        answer = content.get('answer')
        session_id = content.get('session_id')

        target_group = f"messenger_user_{target_user_id}"
        await self.channel_layer.group_send(target_group, {
            'type': 'p2p.answer',
            'from_user_id': self.user_id,
            'from_username': self.user.username,
            'session_id': session_id,
            'answer': answer
        })

    async def handle_p2p_ice(self, content):
        """Forward ICE candidate"""
        target_user_id = content.get('target_user_id')
        candidate = content.get('candidate')
        session_id = content.get('session_id')

        target_group = f"messenger_user_{target_user_id}"
        await self.channel_layer.group_send(target_group, {
            'type': 'p2p.ice',
            'from_user_id': self.user_id,
            'session_id': session_id,
            'candidate': candidate
        })

    async def handle_p2p_message(self, content):
        """Forward P2P message (when P2P fails, fallback to hub relay)"""
        target_user_id = content.get('target_user_id')
        encrypted_message = content.get('message')

        target_group = f"messenger_user_{target_user_id}"
        await self.channel_layer.group_send(target_group, {
            'type': 'p2p.message',
            'from_user_id': self.user_id,
            'from_username': self.user.username,
            'message': encrypted_message
        })

    # ========== Channel Layer Event Handlers ==========

    async def message_new(self, event):
        """New message notification"""
        # Don't send to the sender
        if event.get('sender_id') == self.user_id:
            return

        await self.send_json({
            'type': 'message.new',
            'message_id': event.get('message_id'),
            'conversation_id': event.get('conversation_id'),
            'sender_id': event.get('sender_id'),
            'sender_username': event.get('sender_username'),
            'message_type': event.get('message_type'),
            'created_at': event.get('created_at'),
        })

    async def message_edited(self, event):
        """Message edited notification"""
        await self.send_json({
            'type': 'message.edited',
            'message_id': event.get('message_id'),
            'conversation_id': event.get('conversation_id'),
            'edited_at': event.get('edited_at'),
        })

    async def message_deleted(self, event):
        """Message deleted notification"""
        await self.send_json({
            'type': 'message.deleted',
            'message_id': event.get('message_id'),
            'conversation_id': event.get('conversation_id'),
            'for_everyone': event.get('for_everyone', False),
        })

    async def message_read(self, event):
        """Message read notification"""
        await self.send_json({
            'type': 'message.read',
            'message_id': event.get('message_id'),
            'user_id': event.get('user_id'),
            'username': event.get('username'),
            'read_at': event.get('read_at'),
        })

    async def typing_start(self, event):
        """Typing started notification"""
        # Don't send to the typer
        if event.get('user_id') == self.user_id:
            return

        await self.send_json({
            'type': 'typing.start',
            'conversation_id': event.get('conversation_id'),
            'user_id': event.get('user_id'),
            'username': event.get('username'),
        })

    async def typing_stop(self, event):
        """Typing stopped notification"""
        if event.get('user_id') == self.user_id:
            return

        await self.send_json({
            'type': 'typing.stop',
            'conversation_id': event.get('conversation_id'),
            'user_id': event.get('user_id'),
            'username': event.get('username'),
        })

    async def participant_joined(self, event):
        """Participant joined conversation"""
        await self.send_json({
            'type': 'participant.joined',
            'conversation_id': event.get('conversation_id'),
            'user_id': event.get('user_id'),
            'username': event.get('username'),
        })

    async def participant_left(self, event):
        """Participant left conversation"""
        await self.send_json({
            'type': 'participant.left',
            'conversation_id': event.get('conversation_id'),
            'user_id': event.get('user_id'),
            'username': event.get('username'),
        })

    async def p2p_offer(self, event):
        """P2P offer received"""
        await self.send_json({
            'type': 'p2p.offer',
            'session_id': event.get('session_id'),
            'from_user_id': event.get('from_user_id'),
            'from_username': event.get('from_username'),
            'offer': event.get('offer'),
        })

    async def p2p_answer(self, event):
        """P2P answer received"""
        await self.send_json({
            'type': 'p2p.answer',
            'session_id': event.get('session_id'),
            'from_user_id': event.get('from_user_id'),
            'from_username': event.get('from_username'),
            'answer': event.get('answer'),
        })

    async def p2p_ice(self, event):
        """ICE candidate received"""
        await self.send_json({
            'type': 'p2p.ice',
            'session_id': event.get('session_id'),
            'from_user_id': event.get('from_user_id'),
            'candidate': event.get('candidate'),
        })

    async def p2p_message(self, event):
        """P2P message received (hub relay fallback)"""
        await self.send_json({
            'type': 'p2p.message',
            'from_user_id': event.get('from_user_id'),
            'from_username': event.get('from_username'),
            'message': event.get('message'),
        })

    async def presence_update(self, event):
        """User presence update"""
        await self.send_json({
            'type': 'presence.update',
            'user_id': event.get('user_id'),
            'username': event.get('username'),
            'is_online': event.get('is_online'),
        })

    # ========== Helper Methods ==========

    @database_sync_to_async
    def get_user_conversations(self):
        """Get list of user's conversation IDs"""
        from .models import Participant
        return list(
            Participant.objects.filter(
                user=self.user,
                is_active=True
            ).values_list('conversation_id', flat=True)
        )

    @database_sync_to_async
    def verify_conversation_access(self, conversation_id):
        """Check if user has access to conversation"""
        from .models import Participant
        return Participant.objects.filter(
            conversation_id=conversation_id,
            user=self.user,
            is_active=True
        ).exists()

    @database_sync_to_async
    def mark_message_read(self, message_id):
        """Mark a message as read in database"""
        from .models import Message, MessageReadReceipt, Participant

        try:
            message = Message.objects.get(id=message_id)
            MessageReadReceipt.objects.get_or_create(
                message=message,
                user=self.user
            )
            # Update participant's read status
            Participant.objects.filter(
                conversation=message.conversation,
                user=self.user
            ).update(
                last_read_at=timezone.now(),
                last_read_message_id=message_id
            )
        except Message.DoesNotExist:
            pass

    async def broadcast_presence(self, is_online: bool):
        """Broadcast user's presence to their conversations"""
        for group_name in self.conversation_groups:
            await self.channel_layer.group_send(group_name, {
                'type': 'presence.update',
                'user_id': self.user_id,
                'username': self.user.username,
                'is_online': is_online
            })


# ========== Utility Functions ==========

async def send_message_notification(conversation_id: str, message_data: dict):
    """
    Send message notification to conversation group.

    Call this from views after creating a message.
    """
    from channels.layers import get_channel_layer

    channel_layer = get_channel_layer()
    group_name = f"messenger_conversation_{conversation_id}"

    await channel_layer.group_send(group_name, {
        'type': 'message.new',
        'conversation_id': conversation_id,
        **message_data
    })


def send_message_notification_sync(conversation_id: str, message_data: dict):
    """Synchronous wrapper for send_message_notification"""
    from asgiref.sync import async_to_sync
    from channels.layers import get_channel_layer

    channel_layer = get_channel_layer()
    group_name = f"messenger_conversation_{conversation_id}"

    async_to_sync(channel_layer.group_send)(group_name, {
        'type': 'message.new',
        'conversation_id': conversation_id,
        **message_data
    })
