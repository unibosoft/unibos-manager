/// Messenger Service
///
/// API client for messenger module.
/// Handles conversations, messages, and encryption key management.

import '../api/api_client.dart';
import 'messenger_models.dart';

class MessengerService {
  final ApiClient _apiClient;

  MessengerService(this._apiClient);

  // ========== Conversations ==========

  /// Get list of conversations
  Future<List<Conversation>> getConversations() async {
    final data = await _apiClient.get<List<dynamic>>('/messenger/conversations/');
    return data.map((json) => Conversation.fromJson(json)).toList();
  }

  /// Get conversation details
  Future<Conversation> getConversation(String conversationId) async {
    final data = await _apiClient.get<Map<String, dynamic>>(
      '/messenger/conversations/$conversationId/',
    );
    return Conversation.fromJson(data);
  }

  /// Create new conversation
  Future<Conversation> createConversation({
    required List<String> participantIds,
    String type = 'direct',
    String? name,
    String? description,
    bool isEncrypted = true,
    String transportMode = 'hub',
    bool p2pEnabled = false,
  }) async {
    final data = await _apiClient.post<Map<String, dynamic>>(
      '/messenger/conversations/',
      data: {
        'conversation_type': type,
        'participant_ids': participantIds,
        if (name != null) 'name': name,
        if (description != null) 'description': description,
        'is_encrypted': isEncrypted,
        'transport_mode': transportMode,
        'p2p_enabled': p2pEnabled,
      },
    );
    return Conversation.fromJson(data);
  }

  /// Update conversation
  Future<Conversation> updateConversation(
    String conversationId, {
    String? name,
    String? description,
    String? transportMode,
    bool? p2pEnabled,
  }) async {
    final data = await _apiClient.patch<Map<String, dynamic>>(
      '/messenger/conversations/$conversationId/',
      data: {
        if (name != null) 'name': name,
        if (description != null) 'description': description,
        if (transportMode != null) 'transport_mode': transportMode,
        if (p2pEnabled != null) 'p2p_enabled': p2pEnabled,
      },
    );
    return Conversation.fromJson(data);
  }

  /// Leave/delete conversation
  Future<void> leaveConversation(String conversationId) async {
    await _apiClient.delete('/messenger/conversations/$conversationId/');
  }

  /// Add participant to conversation
  Future<Participant> addParticipant(
    String conversationId,
    String userId, {
    String role = 'member',
    String? encryptedGroupKey,
  }) async {
    final data = await _apiClient.post<Map<String, dynamic>>(
      '/messenger/conversations/$conversationId/participants/',
      data: {
        'user_id': userId,
        'role': role,
        if (encryptedGroupKey != null) 'encrypted_group_key': encryptedGroupKey,
      },
    );
    return Participant.fromJson(data);
  }

  /// Remove participant from conversation
  Future<void> removeParticipant(String conversationId, String userId) async {
    await _apiClient.delete(
      '/messenger/conversations/$conversationId/participants/$userId/',
    );
  }

  /// Mark all messages as read
  Future<void> markAllRead(String conversationId) async {
    await _apiClient.post('/messenger/conversations/$conversationId/read-all/');
  }

  // ========== Messages ==========

  /// Get messages in conversation
  Future<List<Message>> getMessages(String conversationId, {String? cursor}) async {
    final queryParams = cursor != null ? {'cursor': cursor} : null;
    final data = await _apiClient.get<dynamic>(
      '/messenger/conversations/$conversationId/messages/',
      queryParameters: queryParams,
    );

    // Handle paginated response
    if (data is Map && data.containsKey('results')) {
      final List<dynamic> results = data['results'];
      return results.map((json) => Message.fromJson(json)).toList();
    }

    final List<dynamic> list = data;
    return list.map((json) => Message.fromJson(json)).toList();
  }

  /// Send message
  Future<Message> sendMessage(
    String conversationId, {
    required String encryptedContent,
    required String contentNonce,
    required String signature,
    required String senderKeyId,
    String messageType = 'text',
    String? replyTo,
    String? clientMessageId,
    DateTime? expiresAt,
    String transportMode = 'hub',
  }) async {
    final data = await _apiClient.post<Map<String, dynamic>>(
      '/messenger/conversations/$conversationId/messages/',
      data: {
        'encrypted_content': encryptedContent,
        'content_nonce': contentNonce,
        'signature': signature,
        'sender_key_id': senderKeyId,
        'message_type': messageType,
        if (replyTo != null) 'reply_to': replyTo,
        if (clientMessageId != null) 'client_message_id': clientMessageId,
        if (expiresAt != null) 'expires_at': expiresAt.toIso8601String(),
        'transport_mode': transportMode,
      },
    );
    return Message.fromJson(data);
  }

  /// Edit message
  Future<Message> editMessage(
    String conversationId,
    String messageId, {
    required String encryptedContent,
    required String contentNonce,
    required String signature,
  }) async {
    final data = await _apiClient.patch<Map<String, dynamic>>(
      '/messenger/conversations/$conversationId/messages/$messageId/',
      data: {
        'encrypted_content': encryptedContent,
        'content_nonce': contentNonce,
        'signature': signature,
      },
    );
    return Message.fromJson(data);
  }

  /// Delete message
  Future<void> deleteMessage(
    String conversationId,
    String messageId, {
    bool forEveryone = false,
  }) async {
    await _apiClient.delete(
      '/messenger/conversations/$conversationId/messages/$messageId/',
      queryParameters: {'for_everyone': forEveryone.toString()},
    );
  }

  /// Mark message as read
  Future<void> markMessageRead(
    String conversationId,
    String messageId, {
    String? deviceId,
  }) async {
    await _apiClient.post(
      '/messenger/conversations/$conversationId/messages/$messageId/read/',
      data: {if (deviceId != null) 'device_id': deviceId},
    );
  }

  /// Add reaction to message
  Future<MessageReaction> addReaction(
    String conversationId,
    String messageId,
    String emoji,
  ) async {
    final data = await _apiClient.post<Map<String, dynamic>>(
      '/messenger/conversations/$conversationId/messages/$messageId/reactions/',
      data: {'emoji': emoji},
    );
    return MessageReaction.fromJson(data);
  }

  /// Remove reaction from message
  Future<void> removeReaction(
    String conversationId,
    String messageId,
    String emoji,
  ) async {
    await _apiClient.delete(
      '/messenger/conversations/$conversationId/messages/$messageId/reactions/',
      queryParameters: {'emoji': emoji},
    );
  }

  // ========== Encryption Keys ==========

  /// Generate new key pair
  Future<KeyGenerationResult> generateKeys({
    required String deviceId,
    String? deviceName,
    bool setAsPrimary = false,
  }) async {
    final data = await _apiClient.post<Map<String, dynamic>>(
      '/messenger/keys/generate/',
      data: {
        'device_id': deviceId,
        'device_name': deviceName ?? '',
        'set_as_primary': setAsPrimary,
      },
    );
    return KeyGenerationResult.fromJson(data);
  }

  /// Get user's keys
  Future<List<UserEncryptionKey>> getMyKeys() async {
    final data = await _apiClient.get<List<dynamic>>('/messenger/keys/');
    return data.map((json) => UserEncryptionKey.fromJson(json)).toList();
  }

  /// Get another user's public keys
  Future<List<UserEncryptionKey>> getUserPublicKeys(String userId) async {
    final data = await _apiClient.get<List<dynamic>>(
      '/messenger/keys/public/$userId/',
    );
    return data.map((json) => UserEncryptionKey.fromJson(json)).toList();
  }

  /// Revoke key
  Future<void> revokeKey(String keyId) async {
    await _apiClient.post('/messenger/keys/$keyId/revoke/');
  }

  // ========== P2P ==========

  /// Get P2P status
  Future<List<P2PSession>> getP2PStatus() async {
    final data = await _apiClient.get<List<dynamic>>('/messenger/p2p/status/');
    return data.map((json) => P2PSession.fromJson(json)).toList();
  }

  /// Initiate P2P connection
  Future<P2PSession> connectP2P(
    String peerUserId, {
    String? conversationId,
    Map<String, dynamic>? connectionOffer,
  }) async {
    final data = await _apiClient.post<Map<String, dynamic>>(
      '/messenger/p2p/connect/',
      data: {
        'peer_user_id': peerUserId,
        if (conversationId != null) 'conversation_id': conversationId,
        if (connectionOffer != null) 'connection_offer': connectionOffer,
      },
    );
    return P2PSession.fromJson(data);
  }

  /// Answer P2P connection
  Future<P2PSession> answerP2P(
    String sessionId,
    Map<String, dynamic> connectionAnswer,
  ) async {
    final data = await _apiClient.post<Map<String, dynamic>>(
      '/messenger/p2p/answer/',
      data: {
        'session_id': sessionId,
        'connection_answer': connectionAnswer,
      },
    );
    return P2PSession.fromJson(data);
  }

  /// Disconnect P2P session
  Future<void> disconnectP2P(String sessionId) async {
    await _apiClient.post('/messenger/p2p/disconnect/$sessionId/');
  }

  // ========== Typing ==========

  /// Send typing indicator
  Future<void> sendTypingIndicator(String conversationId, bool isTyping) async {
    await _apiClient.post(
      '/messenger/typing/',
      data: {
        'conversation_id': conversationId,
        'is_typing': isTyping,
      },
    );
  }

  // ========== Search ==========

  /// Search messages
  Future<SearchResult> searchMessages({
    String? conversationId,
    DateTime? before,
    DateTime? after,
    String? senderId,
    String? messageType,
    bool? hasAttachments,
    int limit = 50,
    int offset = 0,
  }) async {
    final data = await _apiClient.post<Map<String, dynamic>>(
      '/messenger/search/',
      data: {
        if (conversationId != null) 'conversation_id': conversationId,
        if (before != null) 'before': before.toIso8601String(),
        if (after != null) 'after': after.toIso8601String(),
        if (senderId != null) 'sender_id': senderId,
        if (messageType != null) 'message_type': messageType,
        if (hasAttachments != null) 'has_attachments': hasAttachments,
        'limit': limit,
        'offset': offset,
      },
    );
    return SearchResult.fromJson(data);
  }
}

/// Result of key generation
class KeyGenerationResult {
  final String keyId;
  final String deviceId;
  final String publicKey;
  final String privateKey;
  final String signingPublicKey;
  final String signingPrivateKey;
  final String message;

  KeyGenerationResult({
    required this.keyId,
    required this.deviceId,
    required this.publicKey,
    required this.privateKey,
    required this.signingPublicKey,
    required this.signingPrivateKey,
    required this.message,
  });

  factory KeyGenerationResult.fromJson(Map<String, dynamic> json) {
    return KeyGenerationResult(
      keyId: json['key_id'],
      deviceId: json['device_id'],
      publicKey: json['public_key'],
      privateKey: json['private_key'],
      signingPublicKey: json['signing_public_key'],
      signingPrivateKey: json['signing_private_key'],
      message: json['message'] ?? '',
    );
  }
}

/// Search result
class SearchResult {
  final List<Message> messages;
  final int offset;
  final int limit;
  final int total;

  SearchResult({
    required this.messages,
    required this.offset,
    required this.limit,
    required this.total,
  });

  factory SearchResult.fromJson(Map<String, dynamic> json) {
    return SearchResult(
      messages: (json['messages'] as List)
          .map((m) => Message.fromJson(m))
          .toList(),
      offset: json['offset'],
      limit: json['limit'],
      total: json['total'],
    );
  }
}
