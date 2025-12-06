"""
Messenger Module Views

REST API endpoints for conversations, messages, and encryption.
All messages are encrypted end-to-end.
"""

import logging
from django.db import transaction
from django.db.models import Q, F
from django.utils import timezone
from django.shortcuts import get_object_or_404
from rest_framework import status, generics
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ViewSet
from rest_framework.pagination import CursorPagination

from .models import (
    Conversation,
    Participant,
    Message,
    MessageAttachment,
    MessageReaction,
    MessageReadReceipt,
    UserEncryptionKey,
    P2PSession,
    MessageDeliveryQueue,
)
from .serializers import (
    ConversationSerializer,
    ConversationCreateSerializer,
    ConversationListSerializer,
    ConversationUpdateSerializer,
    ParticipantSerializer,
    ParticipantAddSerializer,
    MessageSerializer,
    MessageCreateSerializer,
    MessageEditSerializer,
    MessageListSerializer,
    MessageAttachmentSerializer,
    AttachmentUploadSerializer,
    MessageReactionSerializer,
    AddReactionSerializer,
    UserEncryptionKeySerializer,
    UserPublicKeySerializer,
    KeyGenerationSerializer,
    P2PSessionSerializer,
    P2PConnectSerializer,
    P2PAnswerSerializer,
    TypingIndicatorSerializer,
    MessageSearchSerializer,
)
from .encryption import get_encryption_service

logger = logging.getLogger('messenger')


# ========== Pagination ==========

class MessagePagination(CursorPagination):
    """Cursor-based pagination for messages"""
    page_size = 50
    ordering = '-created_at'
    cursor_query_param = 'cursor'


# ========== Encryption Key Views ==========

class KeyGenerateView(APIView):
    """Generate new encryption key pair for user"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = KeyGenerationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        device_id = serializer.validated_data['device_id']
        device_name = serializer.validated_data.get('device_name', '')
        set_as_primary = serializer.validated_data.get('set_as_primary', False)

        # Check if device already has keys
        existing = UserEncryptionKey.objects.filter(
            user=request.user,
            device_id=device_id,
            is_active=True
        ).first()

        if existing:
            return Response(
                {'detail': 'Device already has active keys. Revoke existing keys first.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Generate key pairs
        encryption_service = get_encryption_service()
        keypairs = encryption_service.generate_user_keypairs()

        # Store keys
        # Note: In production, private keys should be encrypted with user's password-derived key
        # Here we store them as-is for simplicity (client should encrypt before sending)
        key = UserEncryptionKey.objects.create(
            user=request.user,
            device_id=device_id,
            device_name=device_name,
            public_key=encryption_service.to_base64(keypairs['encryption'].public_key),
            encrypted_private_key='',  # Client should encrypt and store
            signing_public_key=encryption_service.to_base64(keypairs['signing'].public_key),
            encrypted_signing_private_key='',  # Client should encrypt and store
            is_primary=set_as_primary
        )

        if set_as_primary:
            # Unset other primary keys
            UserEncryptionKey.objects.filter(
                user=request.user,
                is_primary=True
            ).exclude(id=key.id).update(is_primary=False)

        # Return public keys and private keys (client should store privately)
        return Response({
            'key_id': str(key.id),
            'device_id': device_id,
            'public_key': encryption_service.to_base64(keypairs['encryption'].public_key),
            'private_key': encryption_service.to_base64(keypairs['encryption'].private_key),
            'signing_public_key': encryption_service.to_base64(keypairs['signing'].public_key),
            'signing_private_key': encryption_service.to_base64(keypairs['signing'].private_key),
            'message': 'Keys generated. Store private keys securely on device.'
        }, status=status.HTTP_201_CREATED)


class KeyListView(generics.ListAPIView):
    """List user's encryption keys"""
    permission_classes = [IsAuthenticated]
    serializer_class = UserEncryptionKeySerializer

    def get_queryset(self):
        return UserEncryptionKey.objects.filter(
            user=self.request.user,
            is_active=True
        )


class KeyRevokeView(APIView):
    """Revoke an encryption key"""
    permission_classes = [IsAuthenticated]

    def post(self, request, key_id):
        key = get_object_or_404(
            UserEncryptionKey,
            id=key_id,
            user=request.user,
            is_active=True
        )
        key.revoke()
        return Response({'detail': 'Key revoked successfully.'})


class UserPublicKeyView(APIView):
    """Get another user's public keys"""
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        keys = UserEncryptionKey.objects.filter(
            user_id=user_id,
            is_active=True
        ).order_by('-is_primary', '-created_at')

        serializer = UserPublicKeySerializer(keys, many=True)
        return Response(serializer.data)


# ========== Conversation Views ==========

class ConversationViewSet(ViewSet):
    """Conversation CRUD operations"""
    permission_classes = [IsAuthenticated]

    def list(self, request):
        """List user's conversations"""
        conversations = Conversation.objects.filter(
            participants__user=request.user,
            participants__is_active=True,
            is_active=True
        ).distinct().order_by('-last_message_at', '-created_at')

        serializer = ConversationListSerializer(
            conversations,
            many=True,
            context={'request': request}
        )
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        """Get conversation details"""
        conversation = get_object_or_404(
            Conversation,
            id=pk,
            participants__user=request.user,
            participants__is_active=True
        )
        serializer = ConversationSerializer(conversation, context={'request': request})
        return Response(serializer.data)

    @transaction.atomic
    def create(self, request):
        """Create new conversation"""
        serializer = ConversationCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        participant_ids = data['participant_ids']

        # For direct messages, check if conversation already exists
        if data['conversation_type'] == 'direct' and len(participant_ids) == 1:
            other_user_id = participant_ids[0]

            existing = Conversation.objects.filter(
                conversation_type='direct',
                participants__user=request.user
            ).filter(
                participants__user_id=other_user_id
            ).first()

            if existing:
                return Response(
                    ConversationSerializer(existing, context={'request': request}).data,
                    status=status.HTTP_200_OK
                )

        # Create conversation
        conversation = Conversation.objects.create(
            conversation_type=data['conversation_type'],
            name=data.get('name', ''),
            description=data.get('description', ''),
            created_by=request.user,
            is_encrypted=data.get('is_encrypted', True),
            transport_mode=data.get('transport_mode', 'hub'),
            p2p_enabled=data.get('p2p_enabled', False)
        )

        # Add creator as owner
        Participant.objects.create(
            conversation=conversation,
            user=request.user,
            role='owner'
        )

        # Add other participants
        for user_id in participant_ids:
            if str(user_id) != str(request.user.id):
                Participant.objects.create(
                    conversation=conversation,
                    user_id=user_id,
                    role='member'
                )

        logger.info(f"Conversation created: {conversation.id} by {request.user.username}")

        return Response(
            ConversationSerializer(conversation, context={'request': request}).data,
            status=status.HTTP_201_CREATED
        )

    def partial_update(self, request, pk=None):
        """Update conversation"""
        conversation = get_object_or_404(
            Conversation,
            id=pk,
            participants__user=request.user,
            participants__is_active=True
        )

        # Check permission (only owner/admin can update)
        participant = conversation.participants.get(user=request.user)
        if participant.role not in ['owner', 'admin']:
            return Response(
                {'detail': 'Only owner or admin can update conversation.'},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = ConversationUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        for field, value in serializer.validated_data.items():
            setattr(conversation, field, value)
        conversation.save()

        return Response(ConversationSerializer(conversation, context={'request': request}).data)

    def destroy(self, request, pk=None):
        """Leave or delete conversation"""
        conversation = get_object_or_404(
            Conversation,
            id=pk,
            participants__user=request.user,
            participants__is_active=True
        )

        participant = conversation.participants.get(user=request.user)

        if participant.role == 'owner':
            # Owner can delete the whole conversation
            conversation.is_active = False
            conversation.save()
            return Response({'detail': 'Conversation deleted.'})
        else:
            # Others just leave
            participant.leave()
            return Response({'detail': 'Left conversation.'})

    @action(detail=True, methods=['post'])
    def add_participant(self, request, pk=None):
        """Add participant to conversation"""
        conversation = get_object_or_404(
            Conversation,
            id=pk,
            participants__user=request.user,
            participants__is_active=True
        )

        # Check permission
        participant = conversation.participants.get(user=request.user)
        if participant.role not in ['owner', 'admin']:
            return Response(
                {'detail': 'Only owner or admin can add participants.'},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = ParticipantAddSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_id = serializer.validated_data['user_id']

        # Check if already participant
        if conversation.participants.filter(user_id=user_id, is_active=True).exists():
            return Response(
                {'detail': 'User is already a participant.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        new_participant = Participant.objects.create(
            conversation=conversation,
            user_id=user_id,
            role=serializer.validated_data.get('role', 'member'),
            encrypted_group_key=serializer.validated_data.get('encrypted_group_key', '')
        )

        return Response(
            ParticipantSerializer(new_participant).data,
            status=status.HTTP_201_CREATED
        )

    @action(detail=True, methods=['delete'], url_path='participants/(?P<user_id>[^/.]+)')
    def remove_participant(self, request, pk=None, user_id=None):
        """Remove participant from conversation"""
        conversation = get_object_or_404(
            Conversation,
            id=pk,
            participants__user=request.user,
            participants__is_active=True
        )

        # Check permission
        requester = conversation.participants.get(user=request.user)
        if requester.role not in ['owner', 'admin']:
            return Response(
                {'detail': 'Only owner or admin can remove participants.'},
                status=status.HTTP_403_FORBIDDEN
            )

        target = get_object_or_404(
            Participant,
            conversation=conversation,
            user_id=user_id,
            is_active=True
        )

        # Can't remove owner
        if target.role == 'owner':
            return Response(
                {'detail': 'Cannot remove conversation owner.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        target.leave()
        return Response({'detail': 'Participant removed.'})


# ========== Message Views ==========

class MessageViewSet(ViewSet):
    """Message CRUD operations"""
    permission_classes = [IsAuthenticated]
    pagination_class = MessagePagination

    def list(self, request, conversation_id=None):
        """List messages in conversation"""
        conversation = get_object_or_404(
            Conversation,
            id=conversation_id,
            participants__user=request.user,
            participants__is_active=True
        )

        messages = conversation.messages.filter(
            Q(is_deleted=False) | Q(deleted_for_everyone=True)
        ).select_related('sender').prefetch_related(
            'attachments', 'reactions'
        ).order_by('-created_at')

        # Pagination
        paginator = MessagePagination()
        page = paginator.paginate_queryset(messages, request)

        if page is not None:
            serializer = MessageListSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        serializer = MessageListSerializer(messages, many=True)
        return Response(serializer.data)

    @transaction.atomic
    def create(self, request, conversation_id=None):
        """Send a message"""
        conversation = get_object_or_404(
            Conversation,
            id=conversation_id,
            participants__user=request.user,
            participants__is_active=True
        )

        serializer = MessageCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data

        # Check for duplicate (client_message_id)
        if data.get('client_message_id'):
            existing = Message.objects.filter(
                conversation=conversation,
                client_message_id=data['client_message_id']
            ).first()
            if existing:
                return Response(
                    MessageSerializer(existing).data,
                    status=status.HTTP_200_OK
                )

        # Create message
        message = Message.objects.create(
            conversation=conversation,
            sender=request.user,
            message_type=data['message_type'],
            encrypted_content=data['encrypted_content'],
            content_nonce=data['content_nonce'],
            signature=data['signature'],
            sender_key_id=data['sender_key_id'],
            reply_to_id=data.get('reply_to'),
            client_message_id=data.get('client_message_id', ''),
            expires_at=data.get('expires_at'),
            delivered_via=data.get('transport_mode', 'hub'),
            is_delivered=True,
            delivered_at=timezone.now()
        )

        # Update conversation
        conversation.last_message_at = message.created_at
        conversation.save(update_fields=['last_message_at'])

        # Update unread counts for other participants
        Participant.objects.filter(
            conversation=conversation,
            is_active=True
        ).exclude(
            user=request.user
        ).update(
            unread_count=F('unread_count') + 1
        )

        # Queue for offline delivery
        for participant in conversation.participants.filter(is_active=True).exclude(user=request.user):
            MessageDeliveryQueue.objects.create(
                message=message,
                recipient=participant.user,
                expires_at=message.expires_at or (timezone.now() + timezone.timedelta(days=30))
            )

        logger.info(f"Message sent: {message.id} in {conversation.id}")

        # Trigger WebSocket notification (will be handled by consumer)
        self._notify_new_message(conversation, message)

        return Response(
            MessageSerializer(message).data,
            status=status.HTTP_201_CREATED
        )

    def retrieve(self, request, conversation_id=None, pk=None):
        """Get message details"""
        message = get_object_or_404(
            Message,
            id=pk,
            conversation_id=conversation_id,
            conversation__participants__user=request.user
        )
        return Response(MessageSerializer(message).data)

    def partial_update(self, request, conversation_id=None, pk=None):
        """Edit message"""
        message = get_object_or_404(
            Message,
            id=pk,
            conversation_id=conversation_id,
            sender=request.user,
            is_deleted=False
        )

        serializer = MessageEditSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Store original hash if first edit
        if not message.is_edited:
            message.original_content_hash = get_encryption_service().hash_content(
                message.encrypted_content.encode()
            )

        message.encrypted_content = serializer.validated_data['encrypted_content']
        message.content_nonce = serializer.validated_data['content_nonce']
        message.signature = serializer.validated_data['signature']
        message.is_edited = True
        message.edited_at = timezone.now()
        message.save()

        return Response(MessageSerializer(message).data)

    def destroy(self, request, conversation_id=None, pk=None):
        """Delete message"""
        message = get_object_or_404(
            Message,
            id=pk,
            conversation_id=conversation_id,
            sender=request.user
        )

        for_everyone = request.query_params.get('for_everyone', 'false').lower() == 'true'
        message.soft_delete(for_everyone=for_everyone)

        return Response({'detail': 'Message deleted.'})

    @action(detail=True, methods=['post'])
    def read(self, request, conversation_id=None, pk=None):
        """Mark message as read"""
        message = get_object_or_404(
            Message,
            id=pk,
            conversation_id=conversation_id,
            conversation__participants__user=request.user
        )

        # Create read receipt
        receipt, created = MessageReadReceipt.objects.get_or_create(
            message=message,
            user=request.user,
            defaults={'device_id': request.data.get('device_id', '')}
        )

        # Update participant's last read
        participant = message.conversation.participants.get(user=request.user)
        participant.mark_read(message.id)

        return Response({'read_at': receipt.read_at.isoformat()})

    @action(detail=True, methods=['post', 'delete'])
    def reactions(self, request, conversation_id=None, pk=None):
        """Add or remove reaction"""
        message = get_object_or_404(
            Message,
            id=pk,
            conversation_id=conversation_id,
            conversation__participants__user=request.user
        )

        if request.method == 'POST':
            serializer = AddReactionSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            reaction, created = MessageReaction.objects.get_or_create(
                message=message,
                user=request.user,
                emoji=serializer.validated_data['emoji']
            )

            return Response(
                MessageReactionSerializer(reaction).data,
                status=status.HTTP_201_CREATED if created else status.HTTP_200_OK
            )

        elif request.method == 'DELETE':
            emoji = request.query_params.get('emoji')
            if not emoji:
                return Response(
                    {'detail': 'Emoji parameter required.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            MessageReaction.objects.filter(
                message=message,
                user=request.user,
                emoji=emoji
            ).delete()

            return Response({'detail': 'Reaction removed.'})

    def _notify_new_message(self, conversation, message):
        """Send WebSocket notification for new message"""
        try:
            from channels.layers import get_channel_layer
            from asgiref.sync import async_to_sync

            channel_layer = get_channel_layer()
            group_name = f"messenger_conversation_{conversation.id}"

            async_to_sync(channel_layer.group_send)(group_name, {
                'type': 'message.new',
                'message_id': str(message.id),
                'sender_id': str(message.sender.id),
                'sender_username': message.sender.username,
                'message_type': message.message_type,
                'created_at': message.created_at.isoformat(),
            })
        except Exception as e:
            logger.warning(f"Failed to send WebSocket notification: {e}")


# ========== Attachment Views ==========

class AttachmentUploadView(APIView):
    """Upload message attachment"""
    permission_classes = [IsAuthenticated]

    def post(self, request, conversation_id, message_id):
        """Upload attachment for a message"""
        message = get_object_or_404(
            Message,
            id=message_id,
            conversation_id=conversation_id,
            sender=request.user
        )

        serializer = AttachmentUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        uploaded_file = serializer.validated_data['file']

        attachment = MessageAttachment.objects.create(
            message=message,
            file=uploaded_file,
            original_filename=uploaded_file.name,
            file_type=uploaded_file.content_type,
            file_size=uploaded_file.size,
            encrypted_file_key=serializer.validated_data['encrypted_file_key'],
            file_nonce=serializer.validated_data['file_nonce'],
            file_hash=serializer.validated_data['file_hash'],
            encrypted_metadata=serializer.validated_data.get('encrypted_metadata', '')
        )

        return Response(
            MessageAttachmentSerializer(attachment).data,
            status=status.HTTP_201_CREATED
        )


class AttachmentDownloadView(APIView):
    """Download message attachment"""
    permission_classes = [IsAuthenticated]

    def get(self, request, conversation_id, message_id, attachment_id):
        """Download encrypted attachment file"""
        # Verify user is participant in conversation
        attachment = get_object_or_404(
            MessageAttachment,
            id=attachment_id,
            message_id=message_id,
            message__conversation_id=conversation_id,
            message__conversation__participants__user=request.user,
            message__conversation__participants__is_active=True
        )

        # Return attachment metadata and download URL
        from django.http import FileResponse
        import os

        if not attachment.file:
            return Response(
                {'detail': 'File not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Stream the encrypted file
        response = FileResponse(
            attachment.file.open('rb'),
            content_type='application/octet-stream'
        )
        response['Content-Disposition'] = f'attachment; filename="{attachment.original_filename}.enc"'
        response['X-File-Hash'] = attachment.file_hash
        response['X-File-Size'] = str(attachment.file_size)
        response['X-Original-Filename'] = attachment.original_filename
        response['X-File-Type'] = attachment.file_type

        return response


class AttachmentListView(APIView):
    """List attachments for a message"""
    permission_classes = [IsAuthenticated]

    def get(self, request, conversation_id, message_id):
        """Get all attachments for a message"""
        message = get_object_or_404(
            Message,
            id=message_id,
            conversation_id=conversation_id,
            conversation__participants__user=request.user,
            conversation__participants__is_active=True
        )

        attachments = message.attachments.all()
        serializer = MessageAttachmentSerializer(attachments, many=True)
        return Response(serializer.data)


class AttachmentMetadataView(APIView):
    """Get attachment metadata (for decryption)"""
    permission_classes = [IsAuthenticated]

    def get(self, request, conversation_id, message_id, attachment_id):
        """Get attachment metadata including encryption keys"""
        attachment = get_object_or_404(
            MessageAttachment,
            id=attachment_id,
            message_id=message_id,
            message__conversation_id=conversation_id,
            message__conversation__participants__user=request.user,
            message__conversation__participants__is_active=True
        )

        return Response({
            'id': str(attachment.id),
            'original_filename': attachment.original_filename,
            'file_type': attachment.file_type,
            'file_size': attachment.file_size,
            'encrypted_file_key': attachment.encrypted_file_key,
            'file_nonce': attachment.file_nonce,
            'file_hash': attachment.file_hash,
            'encrypted_thumbnail_key': attachment.encrypted_thumbnail_key,
            'encrypted_metadata': attachment.encrypted_metadata,
            'is_processed': attachment.is_processed,
            'created_at': attachment.created_at.isoformat()
        })


# ========== P2P Views ==========

class P2PStatusView(APIView):
    """Get P2P connection status"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Get all active P2P sessions for user"""
        sessions = P2PSession.objects.filter(
            Q(user1=request.user) | Q(user2=request.user),
            status__in=['connecting', 'connected']
        )
        serializer = P2PSessionSerializer(sessions, many=True)
        return Response(serializer.data)


class P2PConnectView(APIView):
    """Initiate P2P connection"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = P2PConnectSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        peer_user_id = serializer.validated_data['peer_user_id']

        # Check if session already exists
        existing = P2PSession.objects.filter(
            Q(user1=request.user, user2_id=peer_user_id) |
            Q(user1_id=peer_user_id, user2=request.user),
            status__in=['initiating', 'connecting', 'connected']
        ).first()

        if existing:
            return Response(
                P2PSessionSerializer(existing).data,
                status=status.HTTP_200_OK
            )

        # Create new session
        session = P2PSession.objects.create(
            user1=request.user,
            user2_id=peer_user_id,
            conversation_id=serializer.validated_data.get('conversation_id'),
            connection_info=serializer.validated_data.get('connection_offer', {}),
            status='initiating'
        )

        # Notify peer via WebSocket
        self._notify_p2p_offer(peer_user_id, session)

        return Response(
            P2PSessionSerializer(session).data,
            status=status.HTTP_201_CREATED
        )

    def _notify_p2p_offer(self, peer_user_id, session):
        """Send P2P offer via WebSocket"""
        try:
            from channels.layers import get_channel_layer
            from asgiref.sync import async_to_sync

            channel_layer = get_channel_layer()
            group_name = f"messenger_user_{peer_user_id}"

            async_to_sync(channel_layer.group_send)(group_name, {
                'type': 'p2p.offer',
                'session_id': str(session.id),
                'from_user_id': str(session.user1.id),
                'from_username': session.user1.username,
                'connection_offer': session.connection_info,
            })
        except Exception as e:
            logger.warning(f"Failed to send P2P offer: {e}")


class P2PAnswerView(APIView):
    """Answer P2P connection"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = P2PAnswerSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        session = get_object_or_404(
            P2PSession,
            id=serializer.validated_data['session_id'],
            user2=request.user,
            status='initiating'
        )

        session.connection_info['answer'] = serializer.validated_data['connection_answer']
        session.status = 'connecting'
        session.save()

        # Notify initiator
        self._notify_p2p_answer(session)

        return Response(P2PSessionSerializer(session).data)

    def _notify_p2p_answer(self, session):
        """Send P2P answer via WebSocket"""
        try:
            from channels.layers import get_channel_layer
            from asgiref.sync import async_to_sync

            channel_layer = get_channel_layer()
            group_name = f"messenger_user_{session.user1.id}"

            async_to_sync(channel_layer.group_send)(group_name, {
                'type': 'p2p.answer',
                'session_id': str(session.id),
                'from_user_id': str(session.user2.id),
                'connection_answer': session.connection_info.get('answer', {}),
            })
        except Exception as e:
            logger.warning(f"Failed to send P2P answer: {e}")


class P2PDisconnectView(APIView):
    """Disconnect P2P session"""
    permission_classes = [IsAuthenticated]

    def post(self, request, session_id):
        session = get_object_or_404(
            P2PSession,
            id=session_id
        )

        if session.user1 != request.user and session.user2 != request.user:
            return Response(
                {'detail': 'Not authorized.'},
                status=status.HTTP_403_FORBIDDEN
            )

        session.disconnect()
        return Response({'detail': 'P2P session disconnected.'})


# ========== Typing Indicator View ==========

class TypingIndicatorView(APIView):
    """Send typing indicator"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = TypingIndicatorSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        conversation_id = serializer.validated_data['conversation_id']
        is_typing = serializer.validated_data['is_typing']

        # Verify user is participant
        if not Participant.objects.filter(
            conversation_id=conversation_id,
            user=request.user,
            is_active=True
        ).exists():
            return Response(
                {'detail': 'Not a participant.'},
                status=status.HTTP_403_FORBIDDEN
            )

        # Send via WebSocket
        try:
            from channels.layers import get_channel_layer
            from asgiref.sync import async_to_sync

            channel_layer = get_channel_layer()
            group_name = f"messenger_conversation_{conversation_id}"

            event_type = 'typing.start' if is_typing else 'typing.stop'
            async_to_sync(channel_layer.group_send)(group_name, {
                'type': event_type,
                'user_id': str(request.user.id),
                'username': request.user.username,
            })
        except Exception as e:
            logger.warning(f"Failed to send typing indicator: {e}")

        return Response({'status': 'sent'})


# ========== Search View ==========

class MessageSearchView(APIView):
    """Search messages"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = MessageSearchSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data

        # Base queryset - user's conversations only
        queryset = Message.objects.filter(
            conversation__participants__user=request.user,
            conversation__participants__is_active=True,
            is_deleted=False
        )

        # Filters
        if data.get('conversation_id'):
            queryset = queryset.filter(conversation_id=data['conversation_id'])

        if data.get('before'):
            queryset = queryset.filter(created_at__lt=data['before'])

        if data.get('after'):
            queryset = queryset.filter(created_at__gt=data['after'])

        if data.get('sender_id'):
            queryset = queryset.filter(sender_id=data['sender_id'])

        if data.get('message_type'):
            queryset = queryset.filter(message_type=data['message_type'])

        if data.get('has_attachments'):
            queryset = queryset.filter(attachments__isnull=False).distinct()

        # Pagination
        offset = data.get('offset', 0)
        limit = data.get('limit', 50)

        messages = queryset.order_by('-created_at')[offset:offset + limit]
        serializer = MessageListSerializer(messages, many=True)

        return Response({
            'messages': serializer.data,
            'offset': offset,
            'limit': limit,
            'total': queryset.count()
        })


# ========== Mark All Read View ==========

class MarkAllReadView(APIView):
    """Mark all messages in conversation as read"""
    permission_classes = [IsAuthenticated]

    def post(self, request, conversation_id):
        participant = get_object_or_404(
            Participant,
            conversation_id=conversation_id,
            user=request.user,
            is_active=True
        )

        participant.last_read_at = timezone.now()
        participant.unread_count = 0
        participant.save(update_fields=['last_read_at', 'unread_count'])

        return Response({'detail': 'All messages marked as read.'})


# ========== Read Receipt Views ==========

class ReadReceiptsView(APIView):
    """Get read receipts for a message"""
    permission_classes = [IsAuthenticated]

    def get(self, request, conversation_id, message_id):
        """Get all read receipts for a message"""
        message = get_object_or_404(
            Message,
            id=message_id,
            conversation_id=conversation_id,
            conversation__participants__user=request.user,
            conversation__participants__is_active=True
        )

        receipts = message.read_receipts.select_related('user').order_by('read_at')

        from .serializers import MessageReadReceiptSerializer
        serializer = MessageReadReceiptSerializer(receipts, many=True)
        return Response(serializer.data)


class BatchReadView(APIView):
    """Mark multiple messages as read at once"""
    permission_classes = [IsAuthenticated]

    def post(self, request, conversation_id):
        """Mark multiple messages as read"""
        message_ids = request.data.get('message_ids', [])
        device_id = request.data.get('device_id', '')

        if not message_ids:
            return Response(
                {'detail': 'message_ids required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Verify user is participant
        participant = get_object_or_404(
            Participant,
            conversation_id=conversation_id,
            user=request.user,
            is_active=True
        )

        # Get valid messages
        messages = Message.objects.filter(
            id__in=message_ids,
            conversation_id=conversation_id,
            is_deleted=False
        )

        # Create read receipts
        read_count = 0
        last_message = None
        for message in messages:
            receipt, created = MessageReadReceipt.objects.get_or_create(
                message=message,
                user=request.user,
                defaults={'device_id': device_id}
            )
            if created:
                read_count += 1
                if not last_message or message.created_at > last_message.created_at:
                    last_message = message

        # Update participant's last read
        if last_message:
            participant.last_read_at = timezone.now()
            participant.last_read_message_id = last_message.id
            participant.unread_count = max(0, participant.unread_count - read_count)
            participant.save(update_fields=['last_read_at', 'last_read_message_id', 'unread_count'])

        # Notify sender via WebSocket
        self._notify_read_receipts(conversation_id, message_ids, request.user)

        return Response({
            'marked_count': read_count,
            'read_at': timezone.now().isoformat()
        })

    def _notify_read_receipts(self, conversation_id, message_ids, reader):
        """Send WebSocket notification for read receipts"""
        try:
            from channels.layers import get_channel_layer
            from asgiref.sync import async_to_sync

            channel_layer = get_channel_layer()
            group_name = f"messenger_conversation_{conversation_id}"

            async_to_sync(channel_layer.group_send)(group_name, {
                'type': 'message.read',
                'message_ids': [str(mid) for mid in message_ids],
                'reader_id': str(reader.id),
                'reader_username': reader.username,
                'read_at': timezone.now().isoformat(),
            })
        except Exception as e:
            logger.warning(f"Failed to send read receipt notification: {e}")


class ReadStatusView(APIView):
    """Get read status for messages"""
    permission_classes = [IsAuthenticated]

    def post(self, request, conversation_id):
        """Get read status for multiple messages"""
        message_ids = request.data.get('message_ids', [])

        if not message_ids:
            return Response(
                {'detail': 'message_ids required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Verify user is participant
        if not Participant.objects.filter(
            conversation_id=conversation_id,
            user=request.user,
            is_active=True
        ).exists():
            return Response(
                {'detail': 'Not a participant.'},
                status=status.HTTP_403_FORBIDDEN
            )

        # Get read counts for each message
        from django.db.models import Count
        read_counts = MessageReadReceipt.objects.filter(
            message_id__in=message_ids
        ).values('message_id').annotate(
            count=Count('id')
        )

        # Get all receipts for detailed view
        receipts = MessageReadReceipt.objects.filter(
            message_id__in=message_ids
        ).select_related('user').order_by('read_at')

        result = {}
        for msg_id in message_ids:
            msg_receipts = [r for r in receipts if str(r.message_id) == str(msg_id)]
            result[str(msg_id)] = {
                'read_count': len(msg_receipts),
                'readers': [
                    {
                        'user_id': str(r.user_id),
                        'username': r.user.username,
                        'read_at': r.read_at.isoformat()
                    }
                    for r in msg_receipts
                ]
            }

        return Response(result)
