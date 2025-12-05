/// Messenger State Provider
///
/// Riverpod providers for messenger state management.

import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/api/api_client.dart';
import '../../../core/messenger/messenger_service.dart';
import '../../../core/messenger/messenger_models.dart';

/// Messenger service provider
final messengerServiceProvider = Provider<MessengerService>((ref) {
  final apiClient = ref.watch(apiClientProvider);
  return MessengerService(apiClient);
});

/// Conversations list provider
final conversationsProvider = FutureProvider<List<Conversation>>((ref) async {
  final service = ref.watch(messengerServiceProvider);
  return service.getConversations();
});

/// Single conversation provider
final conversationProvider = FutureProvider.family<Conversation, String>((ref, id) async {
  final service = ref.watch(messengerServiceProvider);
  return service.getConversation(id);
});

/// Messages for a conversation provider
final messagesProvider = FutureProvider.family<List<Message>, String>((ref, conversationId) async {
  final service = ref.watch(messengerServiceProvider);
  return service.getMessages(conversationId);
});

/// User's encryption keys provider
final userKeysProvider = FutureProvider<List<UserEncryptionKey>>((ref) async {
  final service = ref.watch(messengerServiceProvider);
  return service.getMyKeys();
});

/// P2P sessions status provider
final p2pStatusProvider = FutureProvider<List<P2PSession>>((ref) async {
  final service = ref.watch(messengerServiceProvider);
  return service.getP2PStatus();
});

/// Typing state for conversations
class TypingNotifier extends StateNotifier<Map<String, List<TypingState>>> {
  TypingNotifier() : super({});

  void setTyping(String conversationId, TypingState state) {
    final current = Map<String, List<TypingState>>.from(this.state);
    final conversationTyping = List<TypingState>.from(current[conversationId] ?? []);

    // Remove expired or same user typing states
    conversationTyping.removeWhere((t) => t.isExpired || t.userId == state.userId);
    conversationTyping.add(state);

    current[conversationId] = conversationTyping;
    state = current;
  }

  void clearTyping(String conversationId, String userId) {
    final current = Map<String, List<TypingState>>.from(this.state);
    final conversationTyping = List<TypingState>.from(current[conversationId] ?? []);
    conversationTyping.removeWhere((t) => t.userId == userId);
    current[conversationId] = conversationTyping;
    state = current;
  }

  List<TypingState> getTyping(String conversationId) {
    final typing = state[conversationId] ?? [];
    return typing.where((t) => !t.isExpired).toList();
  }
}

final typingProvider = StateNotifierProvider<TypingNotifier, Map<String, List<TypingState>>>((ref) {
  return TypingNotifier();
});

/// Selected conversation state
final selectedConversationProvider = StateProvider<String?>((ref) => null);

/// Current transport mode preference
enum TransportMode { hub, p2p, hybrid }

final transportModeProvider = StateProvider<TransportMode>((ref) => TransportMode.hub);
