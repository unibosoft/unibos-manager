"""
Messenger Module Models

Security-first encrypted messaging with P2P support.
All messages are encrypted end-to-end by default.
"""

import uuid
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.validators import MinLengthValidator

User = get_user_model()


class UserEncryptionKey(models.Model):
    """
    E2E encryption key pairs for users.

    Each user can have multiple key pairs (one per device).
    Public keys are shared, private keys are encrypted with user's password.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='encryption_keys')

    # Device identification
    device_id = models.CharField(max_length=100, db_index=True)
    device_name = models.CharField(max_length=200, blank=True)

    # Key material (Base64 encoded)
    public_key = models.TextField(help_text="X25519 public key (Base64)")
    encrypted_private_key = models.TextField(
        help_text="X25519 private key encrypted with user's key derivation (Base64)"
    )

    # Signing key pair (Ed25519)
    signing_public_key = models.TextField(help_text="Ed25519 public key for message signing (Base64)")
    encrypted_signing_private_key = models.TextField(
        help_text="Ed25519 private key encrypted (Base64)"
    )

    # Key metadata
    key_version = models.PositiveIntegerField(default=1)
    algorithm = models.CharField(max_length=50, default='X25519+Ed25519')

    # Status
    is_active = models.BooleanField(default=True)
    is_primary = models.BooleanField(default=False)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    last_used_at = models.DateTimeField(null=True, blank=True)
    revoked_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        app_label = 'messenger'
        db_table = 'messenger_user_encryption_keys'
        unique_together = ['user', 'device_id']
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['device_id']),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username}:{self.device_name or self.device_id}"

    def revoke(self):
        """Revoke this key pair"""
        self.is_active = False
        self.revoked_at = timezone.now()
        self.save(update_fields=['is_active', 'revoked_at'])

    def mark_used(self):
        """Update last used timestamp"""
        self.last_used_at = timezone.now()
        self.save(update_fields=['last_used_at'])


class Conversation(models.Model):
    """
    A conversation (chat) between users.

    Supports direct messages (2 users) and group chats (3+ users).
    """
    CONVERSATION_TYPE_CHOICES = [
        ('direct', 'Direct Message'),
        ('group', 'Group Chat'),
        ('channel', 'Channel (broadcast)'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Conversation type
    conversation_type = models.CharField(
        max_length=20,
        choices=CONVERSATION_TYPE_CHOICES,
        default='direct'
    )

    # Group info (for group/channel types)
    name = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    avatar = models.ImageField(upload_to='messenger/avatars/', blank=True, null=True)

    # Creator
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_conversations'
    )

    # Security settings
    is_encrypted = models.BooleanField(default=True, help_text="End-to-end encryption enabled")
    encryption_version = models.PositiveIntegerField(default=1)

    # Transport settings
    TRANSPORT_MODE_CHOICES = [
        ('hub', 'Hub Relay (server-based)'),
        ('p2p', 'P2P Direct (peer-to-peer)'),
        ('hybrid', 'Hybrid (P2P with Hub fallback)'),
    ]
    transport_mode = models.CharField(
        max_length=20,
        choices=TRANSPORT_MODE_CHOICES,
        default='hub'
    )
    p2p_enabled = models.BooleanField(default=False, help_text="Allow P2P connections")

    # Group encryption key (encrypted for each participant)
    group_key_version = models.PositiveIntegerField(default=1)

    # Status
    is_active = models.BooleanField(default=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_message_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        app_label = 'messenger'
        db_table = 'messenger_conversations'
        indexes = [
            models.Index(fields=['conversation_type', 'is_active']),
            models.Index(fields=['created_by']),
            models.Index(fields=['last_message_at']),
        ]
        ordering = ['-last_message_at', '-created_at']

    def __str__(self):
        if self.name:
            return self.name
        if self.conversation_type == 'direct':
            participants = self.participants.all()[:2]
            names = [p.user.username for p in participants]
            return ' & '.join(names) if names else 'Direct Message'
        return f"Conversation {str(self.id)[:8]}"

    def get_other_participant(self, user):
        """For direct chats, get the other user"""
        if self.conversation_type != 'direct':
            return None
        return self.participants.exclude(user=user).first()


class Participant(models.Model):
    """
    A user's membership in a conversation.
    """
    ROLE_CHOICES = [
        ('owner', 'Owner'),
        ('admin', 'Admin'),
        ('member', 'Member'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name='participants'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='messenger_participations'
    )

    # Role in conversation
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='member')

    # Encrypted group key for this participant
    encrypted_group_key = models.TextField(
        blank=True,
        help_text="Group encryption key encrypted with participant's public key"
    )
    group_key_version = models.PositiveIntegerField(default=1)

    # Participant's public key for this conversation (for key exchange)
    public_key_id = models.UUIDField(null=True, blank=True)

    # Notification settings
    is_muted = models.BooleanField(default=False)
    muted_until = models.DateTimeField(null=True, blank=True)
    notification_sound = models.CharField(max_length=50, default='default')

    # Read tracking
    last_read_at = models.DateTimeField(null=True, blank=True)
    last_read_message_id = models.UUIDField(null=True, blank=True)
    unread_count = models.PositiveIntegerField(default=0)

    # Status
    is_active = models.BooleanField(default=True)

    # Timestamps
    joined_at = models.DateTimeField(auto_now_add=True)
    left_at = models.DateTimeField(null=True, blank=True)

    # P2P settings for this participant
    p2p_preferred = models.BooleanField(default=False)

    class Meta:
        app_label = 'messenger'
        db_table = 'messenger_participants'
        unique_together = ['conversation', 'user']
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['conversation', 'is_active']),
            models.Index(fields=['last_read_at']),
        ]
        ordering = ['joined_at']

    def __str__(self):
        return f"{self.user.username} in {self.conversation}"

    def leave(self):
        """Mark participant as left"""
        self.is_active = False
        self.left_at = timezone.now()
        self.save(update_fields=['is_active', 'left_at'])

    def mark_read(self, message_id=None):
        """Mark conversation as read"""
        self.last_read_at = timezone.now()
        if message_id:
            self.last_read_message_id = message_id
        self.unread_count = 0
        self.save(update_fields=['last_read_at', 'last_read_message_id', 'unread_count'])


class Message(models.Model):
    """
    A message in a conversation.

    Content is encrypted end-to-end. The server only sees encrypted blobs.
    """
    MESSAGE_TYPE_CHOICES = [
        ('text', 'Text Message'),
        ('image', 'Image'),
        ('file', 'File Attachment'),
        ('voice', 'Voice Message'),
        ('video', 'Video'),
        ('location', 'Location'),
        ('system', 'System Message'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    sender = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='sent_messages'
    )

    # Message type
    message_type = models.CharField(
        max_length=20,
        choices=MESSAGE_TYPE_CHOICES,
        default='text'
    )

    # Encrypted content (AES-256-GCM)
    encrypted_content = models.TextField(help_text="AES-256-GCM encrypted message content")
    content_nonce = models.CharField(max_length=50, help_text="Encryption nonce (Base64)")

    # Message signature (Ed25519)
    signature = models.TextField(help_text="Ed25519 signature for message verification")

    # Encryption metadata
    encryption_version = models.PositiveIntegerField(default=1)
    sender_key_id = models.UUIDField(help_text="Sender's encryption key ID used")

    # Reply/thread support
    reply_to = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='replies'
    )
    thread_root = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='thread_messages'
    )

    # Edit tracking
    is_edited = models.BooleanField(default=False)
    edited_at = models.DateTimeField(null=True, blank=True)
    original_content_hash = models.CharField(max_length=64, blank=True)

    # Delivery tracking
    is_delivered = models.BooleanField(default=False)
    delivered_at = models.DateTimeField(null=True, blank=True)

    # Deletion (soft delete - keep for sync)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    deleted_for_everyone = models.BooleanField(default=False)

    # Message expiration (disappearing messages)
    expires_at = models.DateTimeField(null=True, blank=True)

    # Transport info
    delivered_via = models.CharField(
        max_length=20,
        choices=[('hub', 'Hub'), ('p2p', 'P2P')],
        default='hub'
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)

    # Client-side message ID (for deduplication)
    client_message_id = models.CharField(max_length=100, blank=True, db_index=True)

    class Meta:
        app_label = 'messenger'
        db_table = 'messenger_messages'
        indexes = [
            models.Index(fields=['conversation', 'created_at']),
            models.Index(fields=['sender', 'created_at']),
            models.Index(fields=['reply_to']),
            models.Index(fields=['client_message_id']),
            models.Index(fields=['expires_at']),
        ]
        ordering = ['created_at']

    def __str__(self):
        sender_name = self.sender.username if self.sender else 'System'
        return f"{sender_name}: {self.message_type} @ {self.created_at}"

    def mark_delivered(self):
        """Mark message as delivered to server"""
        if not self.is_delivered:
            self.is_delivered = True
            self.delivered_at = timezone.now()
            self.save(update_fields=['is_delivered', 'delivered_at'])

    def soft_delete(self, for_everyone=False):
        """Soft delete a message"""
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.deleted_for_everyone = for_everyone
        self.save(update_fields=['is_deleted', 'deleted_at', 'deleted_for_everyone'])


class MessageAttachment(models.Model):
    """
    File attachments for messages.

    Files are encrypted before upload, decryption key is in the message.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    message = models.ForeignKey(
        Message,
        on_delete=models.CASCADE,
        related_name='attachments'
    )

    # File info
    file = models.FileField(upload_to='messenger/attachments/%Y/%m/')
    original_filename = models.CharField(max_length=255)
    file_type = models.CharField(max_length=100)  # MIME type
    file_size = models.PositiveBigIntegerField()  # bytes

    # Encrypted file key (encrypted with message key)
    encrypted_file_key = models.TextField(help_text="AES key for file, encrypted with message key")
    file_nonce = models.CharField(max_length=50)
    file_hash = models.CharField(max_length=128, help_text="SHA-256 hash of encrypted file")

    # Thumbnail (for images/videos)
    thumbnail = models.ImageField(
        upload_to='messenger/thumbnails/%Y/%m/',
        blank=True,
        null=True
    )
    encrypted_thumbnail_key = models.TextField(blank=True)

    # Media metadata (encrypted)
    encrypted_metadata = models.TextField(
        blank=True,
        help_text="Encrypted JSON with width, height, duration, etc."
    )

    # Processing status
    is_processed = models.BooleanField(default=False)
    processing_error = models.TextField(blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'messenger'
        db_table = 'messenger_attachments'
        indexes = [
            models.Index(fields=['message']),
            models.Index(fields=['file_type']),
        ]

    def __str__(self):
        return f"{self.original_filename} ({self.file_type})"


class MessageReaction(models.Model):
    """
    Emoji reactions to messages.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    message = models.ForeignKey(
        Message,
        on_delete=models.CASCADE,
        related_name='reactions'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='message_reactions'
    )

    # Reaction emoji
    emoji = models.CharField(max_length=10)  # Unicode emoji

    # Timestamp
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'messenger'
        db_table = 'messenger_reactions'
        unique_together = ['message', 'user', 'emoji']
        indexes = [
            models.Index(fields=['message']),
        ]

    def __str__(self):
        return f"{self.user.username}: {self.emoji}"


class MessageReadReceipt(models.Model):
    """
    Per-user read receipts for messages.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    message = models.ForeignKey(
        Message,
        on_delete=models.CASCADE,
        related_name='read_receipts'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='read_receipts'
    )

    # Read timestamp
    read_at = models.DateTimeField(auto_now_add=True)

    # Device that read the message
    device_id = models.CharField(max_length=100, blank=True)

    class Meta:
        app_label = 'messenger'
        db_table = 'messenger_read_receipts'
        unique_together = ['message', 'user']
        indexes = [
            models.Index(fields=['message']),
            models.Index(fields=['user', 'read_at']),
        ]

    def __str__(self):
        return f"{self.user.username} read @ {self.read_at}"


class P2PSession(models.Model):
    """
    P2P connection sessions between users.

    Tracks active P2P connections for messaging.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Participants (always 2 for P2P)
    user1 = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='p2p_sessions_as_user1'
    )
    user2 = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='p2p_sessions_as_user2'
    )

    # Related conversation (optional)
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='p2p_sessions'
    )

    # Session state
    STATUS_CHOICES = [
        ('initiating', 'Initiating'),
        ('connecting', 'Connecting'),
        ('connected', 'Connected'),
        ('disconnected', 'Disconnected'),
        ('failed', 'Failed'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='initiating')

    # WebRTC/WebSocket connection info (encrypted)
    connection_info = models.JSONField(default=dict)

    # Session keys (ephemeral, for PFS)
    session_key_version = models.PositiveIntegerField(default=1)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    connected_at = models.DateTimeField(null=True, blank=True)
    disconnected_at = models.DateTimeField(null=True, blank=True)
    last_activity = models.DateTimeField(auto_now=True)

    # Stats
    messages_sent = models.PositiveIntegerField(default=0)
    messages_received = models.PositiveIntegerField(default=0)
    bytes_transferred = models.PositiveBigIntegerField(default=0)

    class Meta:
        app_label = 'messenger'
        db_table = 'messenger_p2p_sessions'
        indexes = [
            models.Index(fields=['user1', 'user2', 'status']),
            models.Index(fields=['status']),
            models.Index(fields=['last_activity']),
        ]
        ordering = ['-last_activity']

    def __str__(self):
        return f"P2P: {self.user1.username} <-> {self.user2.username} ({self.status})"

    def connect(self):
        """Mark session as connected"""
        self.status = 'connected'
        self.connected_at = timezone.now()
        self.save(update_fields=['status', 'connected_at'])

    def disconnect(self):
        """Mark session as disconnected"""
        self.status = 'disconnected'
        self.disconnected_at = timezone.now()
        self.save(update_fields=['status', 'disconnected_at'])


class MessageDeliveryQueue(models.Model):
    """
    Queue for offline message delivery.

    When a user is offline, messages are queued here.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    message = models.ForeignKey(
        Message,
        on_delete=models.CASCADE,
        related_name='delivery_queue'
    )
    recipient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='pending_messages'
    )

    # Delivery status
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('delivered', 'Delivered'),
        ('failed', 'Failed'),
        ('expired', 'Expired'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    # Retry tracking
    retry_count = models.PositiveIntegerField(default=0)
    max_retries = models.PositiveIntegerField(default=5)
    last_retry_at = models.DateTimeField(null=True, blank=True)
    next_retry_at = models.DateTimeField(null=True, blank=True)

    # Failure info
    failure_reason = models.TextField(blank=True)

    # Timestamps
    queued_at = models.DateTimeField(auto_now_add=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField()

    class Meta:
        app_label = 'messenger'
        db_table = 'messenger_delivery_queue'
        indexes = [
            models.Index(fields=['recipient', 'status']),
            models.Index(fields=['status', 'next_retry_at']),
            models.Index(fields=['expires_at']),
        ]
        ordering = ['queued_at']

    def __str__(self):
        return f"Queue: {self.message_id} -> {self.recipient.username} ({self.status})"

    def mark_delivered(self):
        """Mark as delivered"""
        self.status = 'delivered'
        self.delivered_at = timezone.now()
        self.save(update_fields=['status', 'delivered_at'])

    def mark_failed(self, reason=''):
        """Mark delivery as failed"""
        self.status = 'failed'
        self.failure_reason = reason
        self.save(update_fields=['status', 'failure_reason'])
