"""
Messenger Module Signals

Handles post-save events for messaging.
"""

import logging
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone

logger = logging.getLogger('messenger.signals')


@receiver(post_save, sender='messenger.Message')
def message_created(sender, instance, created, **kwargs):
    """Handle new message creation"""
    if not created:
        return

    # Send WebSocket notification
    try:
        from .consumers import send_message_notification_sync

        send_message_notification_sync(
            conversation_id=str(instance.conversation_id),
            message_data={
                'message_id': str(instance.id),
                'sender_id': str(instance.sender.id) if instance.sender else None,
                'sender_username': instance.sender.username if instance.sender else 'System',
                'message_type': instance.message_type,
                'created_at': instance.created_at.isoformat(),
            }
        )
    except Exception as e:
        logger.warning(f"Failed to send message notification: {e}")


@receiver(post_save, sender='messenger.Participant')
def participant_changed(sender, instance, created, **kwargs):
    """Handle participant changes"""
    if created:
        # New participant joined
        try:
            from channels.layers import get_channel_layer
            from asgiref.sync import async_to_sync

            channel_layer = get_channel_layer()
            group_name = f"messenger_conversation_{instance.conversation_id}"

            async_to_sync(channel_layer.group_send)(group_name, {
                'type': 'participant.joined',
                'conversation_id': str(instance.conversation_id),
                'user_id': str(instance.user_id),
                'username': instance.user.username,
            })
        except Exception as e:
            logger.warning(f"Failed to send participant notification: {e}")


@receiver(post_save, sender='messenger.P2PSession')
def p2p_session_changed(sender, instance, **kwargs):
    """Handle P2P session state changes"""
    if instance.status == 'connected':
        logger.info(f"P2P session connected: {instance.user1.username} <-> {instance.user2.username}")
    elif instance.status == 'disconnected':
        logger.info(f"P2P session disconnected: {instance.id}")
