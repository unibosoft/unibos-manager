/// Chat Screen
///
/// Individual conversation view with messages and input.

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../core/theme/colors.dart';
import '../../../core/messenger/messenger_models.dart';
import '../providers/messenger_provider.dart';
import '../widgets/message_bubble.dart';
import '../widgets/message_input.dart';
import '../widgets/typing_indicator.dart';

class ChatScreen extends ConsumerStatefulWidget {
  final String conversationId;

  const ChatScreen({super.key, required this.conversationId});

  @override
  ConsumerState<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends ConsumerState<ChatScreen> {
  final ScrollController _scrollController = ScrollController();
  final TextEditingController _messageController = TextEditingController();
  bool _isTyping = false;

  @override
  void dispose() {
    _scrollController.dispose();
    _messageController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final conversationAsync = ref.watch(conversationProvider(widget.conversationId));
    final messagesAsync = ref.watch(messagesProvider(widget.conversationId));
    final transportMode = ref.watch(transportModeProvider);

    return Scaffold(
      appBar: _buildAppBar(context, conversationAsync, transportMode),
      body: Column(
        children: [
          // Messages list
          Expanded(
            child: messagesAsync.when(
              data: (messages) => _buildMessagesList(messages),
              loading: () => const Center(child: CircularProgressIndicator()),
              error: (error, stack) => _buildErrorState(),
            ),
          ),
          // Typing indicator
          _buildTypingIndicator(),
          // Message input
          MessageInput(
            controller: _messageController,
            onSend: _sendMessage,
            onTypingChanged: _handleTypingChanged,
          ),
        ],
      ),
    );
  }

  PreferredSizeWidget _buildAppBar(
    BuildContext context,
    AsyncValue<Conversation> conversationAsync,
    TransportMode transportMode,
  ) {
    return AppBar(
      leading: IconButton(
        icon: const Icon(Icons.arrow_back),
        onPressed: () => context.pop(),
      ),
      title: conversationAsync.when(
        data: (conversation) => Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              conversation.displayName,
              style: const TextStyle(fontSize: 16),
            ),
            Row(
              children: [
                Icon(
                  conversation.isEncrypted ? Icons.lock : Icons.lock_open,
                  size: 10,
                  color: conversation.isEncrypted
                      ? UnibosColors.green
                      : UnibosColors.textMuted,
                ),
                const SizedBox(width: 4),
                Text(
                  conversation.isEncrypted ? 'encrypted' : 'not encrypted',
                  style: TextStyle(
                    fontSize: 10,
                    color: conversation.isEncrypted
                        ? UnibosColors.green
                        : UnibosColors.textMuted,
                  ),
                ),
                if (conversation.p2pEnabled) ...[
                  const SizedBox(width: 8),
                  const Icon(
                    Icons.wifi_tethering,
                    size: 10,
                    color: UnibosColors.orange,
                  ),
                  const SizedBox(width: 2),
                  const Text(
                    'p2p',
                    style: TextStyle(fontSize: 10, color: UnibosColors.orange),
                  ),
                ],
              ],
            ),
          ],
        ),
        loading: () => const Text('loading...'),
        error: (_, __) => const Text('conversation'),
      ),
      actions: [
        IconButton(
          icon: const Icon(Icons.info_outline, size: 20),
          onPressed: () => _showConversationInfo(context),
        ),
      ],
    );
  }

  Widget _buildMessagesList(List<Message> messages) {
    if (messages.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(
              Icons.chat_bubble_outline,
              size: 48,
              color: UnibosColors.textMuted,
            ),
            const SizedBox(height: 16),
            Text(
              'no messages yet',
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    color: UnibosColors.textMuted,
                  ),
            ),
            const SizedBox(height: 4),
            Text(
              'send a message to start the conversation',
              style: Theme.of(context).textTheme.bodySmall?.copyWith(
                    color: UnibosColors.textMuted,
                  ),
            ),
          ],
        ),
      );
    }

    return ListView.builder(
      controller: _scrollController,
      reverse: true,
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 8),
      itemCount: messages.length,
      itemBuilder: (context, index) {
        final message = messages[index];
        final previousMessage = index < messages.length - 1 ? messages[index + 1] : null;
        final showAvatar = previousMessage == null ||
            previousMessage.sender?.id != message.sender?.id;

        return MessageBubble(
          message: message,
          showAvatar: showAvatar,
          onReply: () => _handleReply(message),
          onReact: (emoji) => _handleReaction(message, emoji),
        );
      },
    );
  }

  Widget _buildTypingIndicator() {
    final typingStates = ref.watch(typingProvider)[widget.conversationId] ?? [];
    final activeTyping = typingStates.where((t) => !t.isExpired).toList();

    if (activeTyping.isEmpty) return const SizedBox.shrink();

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
      alignment: Alignment.centerLeft,
      child: TypingIndicator(
        usernames: activeTyping.map((t) => t.username).toList(),
      ),
    );
  }

  Widget _buildErrorState() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const Icon(Icons.error_outline, size: 48, color: UnibosColors.red),
          const SizedBox(height: 16),
          const Text('failed to load messages'),
          TextButton(
            onPressed: () => ref.invalidate(messagesProvider(widget.conversationId)),
            child: const Text('retry'),
          ),
        ],
      ),
    );
  }

  void _sendMessage() async {
    final text = _messageController.text.trim();
    if (text.isEmpty) return;

    _messageController.clear();

    // TODO: Implement actual message sending with encryption
    // This would involve:
    // 1. Get recipient's public keys
    // 2. Encrypt message content
    // 3. Sign the message
    // 4. Send via API

    final service = ref.read(messengerServiceProvider);
    try {
      // Placeholder - actual implementation needs encryption
      await service.sendMessage(
        widget.conversationId,
        encryptedContent: text, // Would be encrypted
        contentNonce: 'placeholder-nonce',
        signature: 'placeholder-signature',
        senderKeyId: 'placeholder-key-id',
      );
      ref.invalidate(messagesProvider(widget.conversationId));
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('failed to send message: $e')),
        );
      }
    }
  }

  void _handleTypingChanged(bool isTyping) async {
    if (_isTyping == isTyping) return;
    _isTyping = isTyping;

    final service = ref.read(messengerServiceProvider);
    try {
      await service.sendTypingIndicator(widget.conversationId, isTyping);
    } catch (e) {
      // Ignore typing indicator errors
    }
  }

  void _handleReply(Message message) {
    // TODO: Implement reply functionality
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text('replying to ${message.sender?.displayName}')),
    );
  }

  void _handleReaction(Message message, String emoji) async {
    final service = ref.read(messengerServiceProvider);
    try {
      await service.addReaction(widget.conversationId, message.id, emoji);
      ref.invalidate(messagesProvider(widget.conversationId));
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('failed to add reaction: $e')),
        );
      }
    }
  }

  void _showConversationInfo(BuildContext context) {
    context.push('/messenger/chat/${widget.conversationId}/settings');
  }
}
