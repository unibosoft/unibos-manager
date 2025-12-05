"""
Messenger Module Serializers

REST API serializers for conversations, messages, and encryption keys.
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
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

User = get_user_model()


# ========== User Serializers ==========

class UserMinimalSerializer(serializers.ModelSerializer):
    """Minimal user info for message display"""
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name']


class UserPublicKeySerializer(serializers.ModelSerializer):
    """User's public encryption key"""
    class Meta:
        model = UserEncryptionKey
        fields = [
            'id', 'device_id', 'device_name',
            'public_key', 'signing_public_key',
            'key_version', 'is_active', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


# ========== Encryption Key Serializers ==========

class UserEncryptionKeySerializer(serializers.ModelSerializer):
    """Full encryption key info (private fields excluded in responses)"""
    class Meta:
        model = UserEncryptionKey
        fields = [
            'id', 'device_id', 'device_name',
            'public_key', 'encrypted_private_key',
            'signing_public_key', 'encrypted_signing_private_key',
            'key_version', 'algorithm',
            'is_active', 'is_primary',
            'created_at', 'last_used_at'
        ]
        read_only_fields = ['id', 'created_at', 'last_used_at']
        extra_kwargs = {
            'encrypted_private_key': {'write_only': True},
            'encrypted_signing_private_key': {'write_only': True},
        }


class KeyGenerationSerializer(serializers.Serializer):
    """Request to generate new key pair"""
    device_id = serializers.CharField(max_length=100)
    device_name = serializers.CharField(max_length=200, required=False, default='')
    set_as_primary = serializers.BooleanField(default=False)


class KeyExchangeSerializer(serializers.Serializer):
    """Key exchange for establishing encrypted conversation"""
    conversation_id = serializers.UUIDField()
    public_key_id = serializers.UUIDField()


# ========== Participant Serializers ==========

class ParticipantSerializer(serializers.ModelSerializer):
    """Conversation participant info"""
    user = UserMinimalSerializer(read_only=True)
    user_id = serializers.UUIDField(write_only=True, required=False)

    class Meta:
        model = Participant
        fields = [
            'id', 'user', 'user_id', 'role',
            'is_muted', 'muted_until',
            'last_read_at', 'unread_count',
            'is_active', 'joined_at', 'left_at',
            'p2p_preferred'
        ]
        read_only_fields = [
            'id', 'last_read_at', 'unread_count',
            'is_active', 'joined_at', 'left_at'
        ]


class ParticipantAddSerializer(serializers.Serializer):
    """Add participant to conversation"""
    user_id = serializers.UUIDField()
    role = serializers.ChoiceField(
        choices=['admin', 'member'],
        default='member'
    )
    encrypted_group_key = serializers.CharField(required=False)


# ========== Message Attachment Serializers ==========

class MessageAttachmentSerializer(serializers.ModelSerializer):
    """Message attachment info"""
    class Meta:
        model = MessageAttachment
        fields = [
            'id', 'original_filename', 'file_type', 'file_size',
            'encrypted_file_key', 'file_nonce', 'file_hash',
            'thumbnail', 'encrypted_thumbnail_key',
            'is_processed', 'created_at'
        ]
        read_only_fields = ['id', 'is_processed', 'created_at']


class AttachmentUploadSerializer(serializers.Serializer):
    """Upload attachment"""
    file = serializers.FileField()
    encrypted_file_key = serializers.CharField()
    file_nonce = serializers.CharField()
    file_hash = serializers.CharField()
    encrypted_metadata = serializers.CharField(required=False, default='')


# ========== Message Reaction Serializers ==========

class MessageReactionSerializer(serializers.ModelSerializer):
    """Message reaction"""
    user = UserMinimalSerializer(read_only=True)

    class Meta:
        model = MessageReaction
        fields = ['id', 'user', 'emoji', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']


class AddReactionSerializer(serializers.Serializer):
    """Add reaction to message"""
    emoji = serializers.CharField(max_length=10)


# ========== Read Receipt Serializers ==========

class MessageReadReceiptSerializer(serializers.ModelSerializer):
    """Read receipt"""
    user = UserMinimalSerializer(read_only=True)

    class Meta:
        model = MessageReadReceipt
        fields = ['id', 'user', 'read_at', 'device_id']
        read_only_fields = ['id', 'read_at']


# ========== Message Serializers ==========

class MessageSerializer(serializers.ModelSerializer):
    """Full message with all details"""
    sender = UserMinimalSerializer(read_only=True)
    attachments = MessageAttachmentSerializer(many=True, read_only=True)
    reactions = MessageReactionSerializer(many=True, read_only=True)
    reply_to_preview = serializers.SerializerMethodField()
    read_by_count = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = [
            'id', 'conversation', 'sender',
            'message_type', 'encrypted_content', 'content_nonce',
            'signature', 'encryption_version', 'sender_key_id',
            'reply_to', 'reply_to_preview', 'thread_root',
            'is_edited', 'edited_at',
            'is_delivered', 'delivered_at',
            'is_deleted', 'deleted_for_everyone',
            'expires_at', 'delivered_via',
            'created_at', 'client_message_id',
            'attachments', 'reactions', 'read_by_count'
        ]
        read_only_fields = [
            'id', 'sender', 'is_delivered', 'delivered_at',
            'is_deleted', 'created_at', 'attachments',
            'reactions', 'read_by_count'
        ]

    def get_reply_to_preview(self, obj):
        """Get preview of replied message"""
        if not obj.reply_to:
            return None
        return {
            'id': str(obj.reply_to.id),
            'sender': obj.reply_to.sender.username if obj.reply_to.sender else None,
            'message_type': obj.reply_to.message_type,
            # Content is encrypted, client will decrypt if needed
        }

    def get_read_by_count(self, obj):
        """Count of users who read this message"""
        return obj.read_receipts.count()


class MessageCreateSerializer(serializers.Serializer):
    """Create new message"""
    encrypted_content = serializers.CharField()
    content_nonce = serializers.CharField(max_length=50)
    signature = serializers.CharField()
    sender_key_id = serializers.UUIDField()
    message_type = serializers.ChoiceField(
        choices=['text', 'image', 'file', 'voice', 'video', 'location'],
        default='text'
    )
    reply_to = serializers.UUIDField(required=False, allow_null=True)
    client_message_id = serializers.CharField(max_length=100, required=False, default='')
    expires_at = serializers.DateTimeField(required=False, allow_null=True)
    transport_mode = serializers.ChoiceField(
        choices=['hub', 'p2p'],
        default='hub'
    )


class MessageEditSerializer(serializers.Serializer):
    """Edit message"""
    encrypted_content = serializers.CharField()
    content_nonce = serializers.CharField(max_length=50)
    signature = serializers.CharField()


class MessageListSerializer(serializers.ModelSerializer):
    """Lightweight message for list view"""
    sender = UserMinimalSerializer(read_only=True)
    has_attachments = serializers.SerializerMethodField()
    reaction_count = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = [
            'id', 'sender', 'message_type',
            'encrypted_content', 'content_nonce',
            'is_edited', 'is_deleted',
            'created_at', 'has_attachments', 'reaction_count'
        ]

    def get_has_attachments(self, obj):
        return obj.attachments.exists()

    def get_reaction_count(self, obj):
        return obj.reactions.count()


# ========== Conversation Serializers ==========

class ConversationSerializer(serializers.ModelSerializer):
    """Full conversation details"""
    participants = ParticipantSerializer(many=True, read_only=True)
    created_by = UserMinimalSerializer(read_only=True)
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = [
            'id', 'conversation_type', 'name', 'description', 'avatar',
            'created_by', 'is_encrypted', 'encryption_version',
            'transport_mode', 'p2p_enabled', 'group_key_version',
            'is_active', 'created_at', 'updated_at', 'last_message_at',
            'participants', 'last_message', 'unread_count'
        ]
        read_only_fields = [
            'id', 'created_by', 'created_at', 'updated_at',
            'last_message_at', 'participants'
        ]

    def get_last_message(self, obj):
        """Get the most recent message preview"""
        last_msg = obj.messages.order_by('-created_at').first()
        if not last_msg:
            return None
        return {
            'id': str(last_msg.id),
            'sender': last_msg.sender.username if last_msg.sender else None,
            'message_type': last_msg.message_type,
            'created_at': last_msg.created_at.isoformat(),
            'is_deleted': last_msg.is_deleted
        }

    def get_unread_count(self, obj):
        """Get unread count for current user"""
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return 0

        participant = obj.participants.filter(user=request.user, is_active=True).first()
        return participant.unread_count if participant else 0


class ConversationCreateSerializer(serializers.Serializer):
    """Create new conversation"""
    conversation_type = serializers.ChoiceField(
        choices=['direct', 'group', 'channel'],
        default='direct'
    )
    name = serializers.CharField(max_length=200, required=False, default='')
    description = serializers.CharField(required=False, default='')
    participant_ids = serializers.ListField(
        child=serializers.UUIDField(),
        min_length=1
    )
    is_encrypted = serializers.BooleanField(default=True)
    transport_mode = serializers.ChoiceField(
        choices=['hub', 'p2p', 'hybrid'],
        default='hub'
    )
    p2p_enabled = serializers.BooleanField(default=False)


class ConversationListSerializer(serializers.ModelSerializer):
    """Lightweight conversation for list view"""
    other_participant = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = [
            'id', 'conversation_type', 'name', 'avatar',
            'is_encrypted', 'transport_mode', 'p2p_enabled',
            'last_message_at', 'other_participant',
            'last_message', 'unread_count'
        ]

    def get_other_participant(self, obj):
        """For direct chats, get the other user"""
        if obj.conversation_type != 'direct':
            return None

        request = self.context.get('request')
        if not request:
            return None

        other = obj.participants.exclude(user=request.user).first()
        if not other:
            return None

        return {
            'id': str(other.user.id),
            'username': other.user.username,
            'first_name': other.user.first_name,
            'last_name': other.user.last_name
        }

    def get_last_message(self, obj):
        last_msg = obj.messages.order_by('-created_at').first()
        if not last_msg:
            return None
        return {
            'id': str(last_msg.id),
            'sender': last_msg.sender.username if last_msg.sender else None,
            'message_type': last_msg.message_type,
            'created_at': last_msg.created_at.isoformat()
        }

    def get_unread_count(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return 0

        participant = obj.participants.filter(user=request.user, is_active=True).first()
        return participant.unread_count if participant else 0


class ConversationUpdateSerializer(serializers.Serializer):
    """Update conversation"""
    name = serializers.CharField(max_length=200, required=False)
    description = serializers.CharField(required=False)
    transport_mode = serializers.ChoiceField(
        choices=['hub', 'p2p', 'hybrid'],
        required=False
    )
    p2p_enabled = serializers.BooleanField(required=False)


# ========== P2P Session Serializers ==========

class P2PSessionSerializer(serializers.ModelSerializer):
    """P2P session info"""
    user1 = UserMinimalSerializer(read_only=True)
    user2 = UserMinimalSerializer(read_only=True)

    class Meta:
        model = P2PSession
        fields = [
            'id', 'user1', 'user2', 'conversation',
            'status', 'created_at', 'connected_at',
            'disconnected_at', 'last_activity',
            'messages_sent', 'messages_received', 'bytes_transferred'
        ]
        read_only_fields = ['id', 'created_at', 'connected_at', 'disconnected_at']


class P2PConnectSerializer(serializers.Serializer):
    """Initiate P2P connection"""
    peer_user_id = serializers.UUIDField()
    conversation_id = serializers.UUIDField(required=False, allow_null=True)
    connection_offer = serializers.JSONField(required=False)


class P2PAnswerSerializer(serializers.Serializer):
    """Answer P2P connection"""
    session_id = serializers.UUIDField()
    connection_answer = serializers.JSONField()


class P2PIceCandidateSerializer(serializers.Serializer):
    """ICE candidate exchange"""
    session_id = serializers.UUIDField()
    candidate = serializers.JSONField()


# ========== Delivery Queue Serializers ==========

class DeliveryQueueSerializer(serializers.ModelSerializer):
    """Message delivery queue info"""
    message = MessageListSerializer(read_only=True)

    class Meta:
        model = MessageDeliveryQueue
        fields = [
            'id', 'message', 'status',
            'retry_count', 'last_retry_at', 'next_retry_at',
            'failure_reason', 'queued_at', 'delivered_at', 'expires_at'
        ]
        read_only_fields = ['id', 'queued_at', 'delivered_at']


# ========== Typing Indicator Serializers ==========

class TypingIndicatorSerializer(serializers.Serializer):
    """Typing indicator"""
    conversation_id = serializers.UUIDField()
    is_typing = serializers.BooleanField()


# ========== Search Serializers ==========

class MessageSearchSerializer(serializers.Serializer):
    """Search messages (searches encrypted content client-side)"""
    conversation_id = serializers.UUIDField(required=False, allow_null=True)
    before = serializers.DateTimeField(required=False)
    after = serializers.DateTimeField(required=False)
    sender_id = serializers.UUIDField(required=False, allow_null=True)
    message_type = serializers.ChoiceField(
        choices=['text', 'image', 'file', 'voice', 'video', 'location'],
        required=False
    )
    has_attachments = serializers.BooleanField(required=False)
    limit = serializers.IntegerField(default=50, min_value=1, max_value=100)
    offset = serializers.IntegerField(default=0, min_value=0)
