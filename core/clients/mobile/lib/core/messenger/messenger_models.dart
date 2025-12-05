/// Messenger Models
///
/// Data models for messenger module.

import 'package:flutter/foundation.dart';

/// Conversation model
class Conversation {
  final String id;
  final String conversationType;
  final String? name;
  final String? description;
  final String? avatar;
  final UserMinimal? createdBy;
  final bool isEncrypted;
  final int encryptionVersion;
  final String transportMode;
  final bool p2pEnabled;
  final int groupKeyVersion;
  final bool isActive;
  final DateTime createdAt;
  final DateTime updatedAt;
  final DateTime? lastMessageAt;
  final List<Participant> participants;
  final MessagePreview? lastMessage;
  final int unreadCount;

  Conversation({
    required this.id,
    required this.conversationType,
    this.name,
    this.description,
    this.avatar,
    this.createdBy,
    required this.isEncrypted,
    required this.encryptionVersion,
    required this.transportMode,
    required this.p2pEnabled,
    required this.groupKeyVersion,
    required this.isActive,
    required this.createdAt,
    required this.updatedAt,
    this.lastMessageAt,
    required this.participants,
    this.lastMessage,
    required this.unreadCount,
  });

  factory Conversation.fromJson(Map<String, dynamic> json) {
    return Conversation(
      id: json['id'],
      conversationType: json['conversation_type'],
      name: json['name'],
      description: json['description'],
      avatar: json['avatar'],
      createdBy: json['created_by'] != null
          ? UserMinimal.fromJson(json['created_by'])
          : null,
      isEncrypted: json['is_encrypted'] ?? true,
      encryptionVersion: json['encryption_version'] ?? 1,
      transportMode: json['transport_mode'] ?? 'hub',
      p2pEnabled: json['p2p_enabled'] ?? false,
      groupKeyVersion: json['group_key_version'] ?? 1,
      isActive: json['is_active'] ?? true,
      createdAt: DateTime.parse(json['created_at']),
      updatedAt: DateTime.parse(json['updated_at']),
      lastMessageAt: json['last_message_at'] != null
          ? DateTime.parse(json['last_message_at'])
          : null,
      participants: (json['participants'] as List? ?? [])
          .map((p) => Participant.fromJson(p))
          .toList(),
      lastMessage: json['last_message'] != null
          ? MessagePreview.fromJson(json['last_message'])
          : null,
      unreadCount: json['unread_count'] ?? 0,
    );
  }

  /// Get display name for conversation
  String get displayName {
    if (name != null && name!.isNotEmpty) return name!;
    if (conversationType == 'direct' && participants.length == 2) {
      // For direct chats, show other user's name
      return participants
          .map((p) => p.user?.displayName ?? p.user?.username ?? 'Unknown')
          .join(' & ');
    }
    return 'Conversation';
  }

  /// Check if this is a direct message
  bool get isDirect => conversationType == 'direct';

  /// Check if this is a group chat
  bool get isGroup => conversationType == 'group';
}

/// Participant model
class Participant {
  final String id;
  final UserMinimal? user;
  final String role;
  final bool isMuted;
  final DateTime? mutedUntil;
  final DateTime? lastReadAt;
  final int unreadCount;
  final bool isActive;
  final DateTime joinedAt;
  final DateTime? leftAt;
  final bool p2pPreferred;

  Participant({
    required this.id,
    this.user,
    required this.role,
    required this.isMuted,
    this.mutedUntil,
    this.lastReadAt,
    required this.unreadCount,
    required this.isActive,
    required this.joinedAt,
    this.leftAt,
    required this.p2pPreferred,
  });

  factory Participant.fromJson(Map<String, dynamic> json) {
    return Participant(
      id: json['id'],
      user: json['user'] != null ? UserMinimal.fromJson(json['user']) : null,
      role: json['role'] ?? 'member',
      isMuted: json['is_muted'] ?? false,
      mutedUntil: json['muted_until'] != null
          ? DateTime.parse(json['muted_until'])
          : null,
      lastReadAt: json['last_read_at'] != null
          ? DateTime.parse(json['last_read_at'])
          : null,
      unreadCount: json['unread_count'] ?? 0,
      isActive: json['is_active'] ?? true,
      joinedAt: DateTime.parse(json['joined_at']),
      leftAt: json['left_at'] != null ? DateTime.parse(json['left_at']) : null,
      p2pPreferred: json['p2p_preferred'] ?? false,
    );
  }

  bool get isOwner => role == 'owner';
  bool get isAdmin => role == 'admin' || role == 'owner';
}

/// Message model
class Message {
  final String id;
  final String conversationId;
  final UserMinimal? sender;
  final String messageType;
  final String encryptedContent;
  final String contentNonce;
  final String signature;
  final int encryptionVersion;
  final String senderKeyId;
  final String? replyTo;
  final MessagePreview? replyToPreview;
  final String? threadRoot;
  final bool isEdited;
  final DateTime? editedAt;
  final bool isDelivered;
  final DateTime? deliveredAt;
  final bool isDeleted;
  final bool deletedForEveryone;
  final DateTime? expiresAt;
  final String deliveredVia;
  final DateTime createdAt;
  final String? clientMessageId;
  final List<MessageAttachment> attachments;
  final List<MessageReaction> reactions;
  final int readByCount;

  // Decrypted content (set after decryption)
  String? decryptedContent;

  Message({
    required this.id,
    required this.conversationId,
    this.sender,
    required this.messageType,
    required this.encryptedContent,
    required this.contentNonce,
    required this.signature,
    required this.encryptionVersion,
    required this.senderKeyId,
    this.replyTo,
    this.replyToPreview,
    this.threadRoot,
    required this.isEdited,
    this.editedAt,
    required this.isDelivered,
    this.deliveredAt,
    required this.isDeleted,
    required this.deletedForEveryone,
    this.expiresAt,
    required this.deliveredVia,
    required this.createdAt,
    this.clientMessageId,
    required this.attachments,
    required this.reactions,
    required this.readByCount,
    this.decryptedContent,
  });

  factory Message.fromJson(Map<String, dynamic> json) {
    return Message(
      id: json['id'],
      conversationId: json['conversation'] ?? '',
      sender: json['sender'] != null ? UserMinimal.fromJson(json['sender']) : null,
      messageType: json['message_type'] ?? 'text',
      encryptedContent: json['encrypted_content'] ?? '',
      contentNonce: json['content_nonce'] ?? '',
      signature: json['signature'] ?? '',
      encryptionVersion: json['encryption_version'] ?? 1,
      senderKeyId: json['sender_key_id'] ?? '',
      replyTo: json['reply_to'],
      replyToPreview: json['reply_to_preview'] != null
          ? MessagePreview.fromJson(json['reply_to_preview'])
          : null,
      threadRoot: json['thread_root'],
      isEdited: json['is_edited'] ?? false,
      editedAt: json['edited_at'] != null
          ? DateTime.parse(json['edited_at'])
          : null,
      isDelivered: json['is_delivered'] ?? false,
      deliveredAt: json['delivered_at'] != null
          ? DateTime.parse(json['delivered_at'])
          : null,
      isDeleted: json['is_deleted'] ?? false,
      deletedForEveryone: json['deleted_for_everyone'] ?? false,
      expiresAt: json['expires_at'] != null
          ? DateTime.parse(json['expires_at'])
          : null,
      deliveredVia: json['delivered_via'] ?? 'hub',
      createdAt: DateTime.parse(json['created_at']),
      clientMessageId: json['client_message_id'],
      attachments: (json['attachments'] as List? ?? [])
          .map((a) => MessageAttachment.fromJson(a))
          .toList(),
      reactions: (json['reactions'] as List? ?? [])
          .map((r) => MessageReaction.fromJson(r))
          .toList(),
      readByCount: json['read_by_count'] ?? 0,
    );
  }

  bool get isText => messageType == 'text';
  bool get isImage => messageType == 'image';
  bool get isFile => messageType == 'file';
  bool get isVoice => messageType == 'voice';
  bool get isVideo => messageType == 'video';
  bool get isSystem => messageType == 'system';
  bool get hasAttachments => attachments.isNotEmpty;
  bool get isP2P => deliveredVia == 'p2p';
}

/// Message preview (for last message, reply preview)
class MessagePreview {
  final String id;
  final String? sender;
  final String messageType;
  final DateTime? createdAt;
  final bool isDeleted;

  MessagePreview({
    required this.id,
    this.sender,
    required this.messageType,
    this.createdAt,
    required this.isDeleted,
  });

  factory MessagePreview.fromJson(Map<String, dynamic> json) {
    return MessagePreview(
      id: json['id'],
      sender: json['sender'],
      messageType: json['message_type'] ?? 'text',
      createdAt: json['created_at'] != null
          ? DateTime.parse(json['created_at'])
          : null,
      isDeleted: json['is_deleted'] ?? false,
    );
  }
}

/// Message attachment
class MessageAttachment {
  final String id;
  final String originalFilename;
  final String fileType;
  final int fileSize;
  final String encryptedFileKey;
  final String fileNonce;
  final String fileHash;
  final String? thumbnail;
  final String? encryptedThumbnailKey;
  final bool isProcessed;
  final DateTime createdAt;

  MessageAttachment({
    required this.id,
    required this.originalFilename,
    required this.fileType,
    required this.fileSize,
    required this.encryptedFileKey,
    required this.fileNonce,
    required this.fileHash,
    this.thumbnail,
    this.encryptedThumbnailKey,
    required this.isProcessed,
    required this.createdAt,
  });

  factory MessageAttachment.fromJson(Map<String, dynamic> json) {
    return MessageAttachment(
      id: json['id'],
      originalFilename: json['original_filename'] ?? '',
      fileType: json['file_type'] ?? '',
      fileSize: json['file_size'] ?? 0,
      encryptedFileKey: json['encrypted_file_key'] ?? '',
      fileNonce: json['file_nonce'] ?? '',
      fileHash: json['file_hash'] ?? '',
      thumbnail: json['thumbnail'],
      encryptedThumbnailKey: json['encrypted_thumbnail_key'],
      isProcessed: json['is_processed'] ?? false,
      createdAt: DateTime.parse(json['created_at']),
    );
  }

  bool get isImage => fileType.startsWith('image/');
  bool get isVideo => fileType.startsWith('video/');
  bool get isAudio => fileType.startsWith('audio/');

  String get fileSizeFormatted {
    if (fileSize < 1024) return '$fileSize B';
    if (fileSize < 1024 * 1024) return '${(fileSize / 1024).toStringAsFixed(1)} KB';
    return '${(fileSize / (1024 * 1024)).toStringAsFixed(1)} MB';
  }
}

/// Message reaction
class MessageReaction {
  final String id;
  final UserMinimal? user;
  final String emoji;
  final DateTime createdAt;

  MessageReaction({
    required this.id,
    this.user,
    required this.emoji,
    required this.createdAt,
  });

  factory MessageReaction.fromJson(Map<String, dynamic> json) {
    return MessageReaction(
      id: json['id'],
      user: json['user'] != null ? UserMinimal.fromJson(json['user']) : null,
      emoji: json['emoji'],
      createdAt: DateTime.parse(json['created_at']),
    );
  }
}

/// User encryption key
class UserEncryptionKey {
  final String id;
  final String deviceId;
  final String? deviceName;
  final String publicKey;
  final String signingPublicKey;
  final int keyVersion;
  final bool isActive;
  final bool isPrimary;
  final DateTime createdAt;
  final DateTime? lastUsedAt;

  UserEncryptionKey({
    required this.id,
    required this.deviceId,
    this.deviceName,
    required this.publicKey,
    required this.signingPublicKey,
    required this.keyVersion,
    required this.isActive,
    required this.isPrimary,
    required this.createdAt,
    this.lastUsedAt,
  });

  factory UserEncryptionKey.fromJson(Map<String, dynamic> json) {
    return UserEncryptionKey(
      id: json['id'],
      deviceId: json['device_id'],
      deviceName: json['device_name'],
      publicKey: json['public_key'],
      signingPublicKey: json['signing_public_key'],
      keyVersion: json['key_version'] ?? 1,
      isActive: json['is_active'] ?? true,
      isPrimary: json['is_primary'] ?? false,
      createdAt: DateTime.parse(json['created_at']),
      lastUsedAt: json['last_used_at'] != null
          ? DateTime.parse(json['last_used_at'])
          : null,
    );
  }
}

/// P2P session
class P2PSession {
  final String id;
  final UserMinimal? user1;
  final UserMinimal? user2;
  final String? conversationId;
  final String status;
  final DateTime createdAt;
  final DateTime? connectedAt;
  final DateTime? disconnectedAt;
  final DateTime lastActivity;
  final int messagesSent;
  final int messagesReceived;
  final int bytesTransferred;

  P2PSession({
    required this.id,
    this.user1,
    this.user2,
    this.conversationId,
    required this.status,
    required this.createdAt,
    this.connectedAt,
    this.disconnectedAt,
    required this.lastActivity,
    required this.messagesSent,
    required this.messagesReceived,
    required this.bytesTransferred,
  });

  factory P2PSession.fromJson(Map<String, dynamic> json) {
    return P2PSession(
      id: json['id'],
      user1: json['user1'] != null ? UserMinimal.fromJson(json['user1']) : null,
      user2: json['user2'] != null ? UserMinimal.fromJson(json['user2']) : null,
      conversationId: json['conversation'],
      status: json['status'] ?? 'disconnected',
      createdAt: DateTime.parse(json['created_at']),
      connectedAt: json['connected_at'] != null
          ? DateTime.parse(json['connected_at'])
          : null,
      disconnectedAt: json['disconnected_at'] != null
          ? DateTime.parse(json['disconnected_at'])
          : null,
      lastActivity: DateTime.parse(json['last_activity']),
      messagesSent: json['messages_sent'] ?? 0,
      messagesReceived: json['messages_received'] ?? 0,
      bytesTransferred: json['bytes_transferred'] ?? 0,
    );
  }

  bool get isConnected => status == 'connected';
  bool get isConnecting => status == 'connecting' || status == 'initiating';
}

/// Minimal user info
class UserMinimal {
  final String id;
  final String username;
  final String? firstName;
  final String? lastName;

  UserMinimal({
    required this.id,
    required this.username,
    this.firstName,
    this.lastName,
  });

  factory UserMinimal.fromJson(Map<String, dynamic> json) {
    return UserMinimal(
      id: json['id'],
      username: json['username'],
      firstName: json['first_name'],
      lastName: json['last_name'],
    );
  }

  String get displayName {
    if (firstName != null && firstName!.isNotEmpty) {
      if (lastName != null && lastName!.isNotEmpty) {
        return '$firstName $lastName';
      }
      return firstName!;
    }
    return username;
  }

  String get initials {
    if (firstName != null && firstName!.isNotEmpty) {
      String init = firstName![0].toUpperCase();
      if (lastName != null && lastName!.isNotEmpty) {
        init += lastName![0].toUpperCase();
      }
      return init;
    }
    return username.substring(0, 1).toUpperCase();
  }
}

/// Typing indicator state
class TypingState {
  final String conversationId;
  final String userId;
  final String username;
  final DateTime timestamp;

  TypingState({
    required this.conversationId,
    required this.userId,
    required this.username,
    required this.timestamp,
  });

  bool get isExpired => DateTime.now().difference(timestamp).inSeconds > 5;
}
