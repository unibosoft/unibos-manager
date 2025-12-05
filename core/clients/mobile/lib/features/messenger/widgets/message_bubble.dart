/// Message Bubble Widget
///
/// Displays a single message in the chat.

import 'package:flutter/material.dart';
import '../../../core/theme/colors.dart';
import '../../../core/messenger/messenger_models.dart';

class MessageBubble extends StatelessWidget {
  final Message message;
  final bool showAvatar;
  final VoidCallback? onReply;
  final Function(String)? onReact;
  final bool isOwnMessage;

  const MessageBubble({
    super.key,
    required this.message,
    this.showAvatar = true,
    this.onReply,
    this.onReact,
    this.isOwnMessage = false,
  });

  @override
  Widget build(BuildContext context) {
    if (message.isSystem) {
      return _buildSystemMessage(context);
    }

    return Padding(
      padding: EdgeInsets.only(
        top: showAvatar ? 8 : 2,
        bottom: 2,
      ),
      child: Row(
        mainAxisAlignment:
            isOwnMessage ? MainAxisAlignment.end : MainAxisAlignment.start,
        crossAxisAlignment: CrossAxisAlignment.end,
        children: [
          // Avatar (other's messages)
          if (!isOwnMessage && showAvatar)
            _buildAvatar()
          else if (!isOwnMessage)
            const SizedBox(width: 40),

          const SizedBox(width: 8),

          // Message content
          Flexible(
            child: GestureDetector(
              onLongPress: () => _showMessageOptions(context),
              child: Container(
                constraints: BoxConstraints(
                  maxWidth: MediaQuery.of(context).size.width * 0.75,
                ),
                child: Column(
                  crossAxisAlignment: isOwnMessage
                      ? CrossAxisAlignment.end
                      : CrossAxisAlignment.start,
                  children: [
                    // Sender name (group chats)
                    if (!isOwnMessage && showAvatar)
                      Padding(
                        padding: const EdgeInsets.only(left: 12, bottom: 2),
                        child: Text(
                          message.sender?.displayName ?? 'Unknown',
                          style: const TextStyle(
                            fontSize: 11,
                            color: UnibosColors.orange,
                            fontWeight: FontWeight.w500,
                          ),
                        ),
                      ),

                    // Reply preview
                    if (message.replyToPreview != null)
                      _buildReplyPreview(context),

                    // Message bubble
                    Container(
                      padding: const EdgeInsets.symmetric(
                        horizontal: 12,
                        vertical: 8,
                      ),
                      decoration: BoxDecoration(
                        color: isOwnMessage
                            ? UnibosColors.orange.withValues(alpha: 0.2)
                            : UnibosColors.bgDark,
                        borderRadius: BorderRadius.only(
                          topLeft: const Radius.circular(16),
                          topRight: const Radius.circular(16),
                          bottomLeft: Radius.circular(isOwnMessage ? 16 : 4),
                          bottomRight: Radius.circular(isOwnMessage ? 4 : 16),
                        ),
                      ),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          // Message content
                          _buildContent(context),

                          const SizedBox(height: 4),

                          // Footer (time, delivery status)
                          _buildFooter(context),
                        ],
                      ),
                    ),

                    // Reactions
                    if (message.reactions.isNotEmpty) _buildReactions(context),
                  ],
                ),
              ),
            ),
          ),

          const SizedBox(width: 8),

          // Avatar placeholder (own messages)
          if (isOwnMessage) const SizedBox(width: 40),
        ],
      ),
    );
  }

  Widget _buildAvatar() {
    return CircleAvatar(
      radius: 16,
      backgroundColor: UnibosColors.orange,
      child: Text(
        message.sender?.initials ?? '?',
        style: const TextStyle(
          color: Colors.white,
          fontSize: 10,
          fontWeight: FontWeight.bold,
        ),
      ),
    );
  }

  Widget _buildContent(BuildContext context) {
    if (message.isDeleted) {
      return Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          const Icon(
            Icons.block,
            size: 14,
            color: UnibosColors.textMuted,
          ),
          const SizedBox(width: 4),
          Text(
            'message deleted',
            style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                  color: UnibosColors.textMuted,
                  fontStyle: FontStyle.italic,
                ),
          ),
        ],
      );
    }

    // For encrypted messages, show decrypted content or placeholder
    final content = message.decryptedContent ?? 'encrypted message';

    switch (message.messageType) {
      case 'text':
        return Text(
          content,
          style: Theme.of(context).textTheme.bodyMedium,
        );
      case 'image':
        return _buildImageMessage(context);
      case 'file':
        return _buildFileMessage(context);
      case 'voice':
        return _buildVoiceMessage(context);
      case 'video':
        return _buildVideoMessage(context);
      default:
        return Text(
          content,
          style: Theme.of(context).textTheme.bodyMedium,
        );
    }
  }

  Widget _buildImageMessage(BuildContext context) {
    if (message.attachments.isEmpty) {
      return const Text('image');
    }

    final attachment = message.attachments.first;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        ClipRRect(
          borderRadius: BorderRadius.circular(8),
          child: Container(
            constraints: const BoxConstraints(maxHeight: 200),
            color: UnibosColors.bgBlack,
            child: attachment.thumbnail != null
                ? Image.network(
                    attachment.thumbnail!,
                    fit: BoxFit.cover,
                  )
                : const Center(
                    child: Icon(Icons.image, size: 48),
                  ),
          ),
        ),
      ],
    );
  }

  Widget _buildFileMessage(BuildContext context) {
    if (message.attachments.isEmpty) {
      return const Text('file');
    }

    final attachment = message.attachments.first;
    return Container(
      padding: const EdgeInsets.all(8),
      decoration: BoxDecoration(
        color: UnibosColors.bgBlack.withValues(alpha: 0.5),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          const Icon(Icons.insert_drive_file, size: 32),
          const SizedBox(width: 8),
          Flexible(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  attachment.originalFilename,
                  style: const TextStyle(fontWeight: FontWeight.w500),
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                ),
                Text(
                  attachment.fileSizeFormatted,
                  style: const TextStyle(
                    fontSize: 12,
                    color: UnibosColors.textMuted,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildVoiceMessage(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(8),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          const Icon(Icons.play_circle_fill, size: 32, color: UnibosColors.orange),
          const SizedBox(width: 8),
          Container(
            width: 100,
            height: 24,
            decoration: BoxDecoration(
              color: UnibosColors.bgBlack.withValues(alpha: 0.5),
              borderRadius: BorderRadius.circular(12),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildVideoMessage(BuildContext context) {
    return Stack(
      alignment: Alignment.center,
      children: [
        ClipRRect(
          borderRadius: BorderRadius.circular(8),
          child: Container(
            height: 150,
            color: UnibosColors.bgBlack,
          ),
        ),
        const Icon(Icons.play_circle_fill, size: 48, color: Colors.white70),
      ],
    );
  }

  Widget _buildFooter(BuildContext context) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        // Edited indicator
        if (message.isEdited)
          const Padding(
            padding: EdgeInsets.only(right: 4),
            child: Text(
              'edited',
              style: TextStyle(fontSize: 10, color: UnibosColors.textMuted),
            ),
          ),

        // P2P indicator
        if (message.isP2P)
          const Padding(
            padding: EdgeInsets.only(right: 4),
            child: Icon(
              Icons.wifi_tethering,
              size: 10,
              color: UnibosColors.orange,
            ),
          ),

        // Time
        Text(
          _formatTime(message.createdAt),
          style: const TextStyle(fontSize: 10, color: UnibosColors.textMuted),
        ),

        // Delivery status (own messages)
        if (isOwnMessage) ...[
          const SizedBox(width: 4),
          Icon(
            message.isDelivered ? Icons.done_all : Icons.done,
            size: 12,
            color: message.isDelivered
                ? UnibosColors.green
                : UnibosColors.textMuted,
          ),
        ],
      ],
    );
  }

  Widget _buildReplyPreview(BuildContext context) {
    return Container(
      margin: const EdgeInsets.only(bottom: 4),
      padding: const EdgeInsets.all(8),
      decoration: BoxDecoration(
        color: UnibosColors.bgBlack.withValues(alpha: 0.3),
        borderRadius: BorderRadius.circular(8),
        border: Border(
          left: BorderSide(
            color: UnibosColors.orange.withValues(alpha: 0.5),
            width: 2,
          ),
        ),
      ),
      child: Text(
        'reply to message',
        style: Theme.of(context).textTheme.bodySmall?.copyWith(
              color: UnibosColors.textMuted,
            ),
        maxLines: 1,
        overflow: TextOverflow.ellipsis,
      ),
    );
  }

  Widget _buildReactions(BuildContext context) {
    // Group reactions by emoji
    final reactionCounts = <String, int>{};
    for (final reaction in message.reactions) {
      reactionCounts[reaction.emoji] = (reactionCounts[reaction.emoji] ?? 0) + 1;
    }

    return Padding(
      padding: const EdgeInsets.only(top: 4),
      child: Wrap(
        spacing: 4,
        children: reactionCounts.entries.map((entry) {
          return Container(
            padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
            decoration: BoxDecoration(
              color: UnibosColors.bgDark,
              borderRadius: BorderRadius.circular(10),
            ),
            child: Text(
              '${entry.key} ${entry.value}',
              style: const TextStyle(fontSize: 12),
            ),
          );
        }).toList(),
      ),
    );
  }

  Widget _buildSystemMessage(BuildContext context) {
    return Center(
      child: Container(
        margin: const EdgeInsets.symmetric(vertical: 8),
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
        decoration: BoxDecoration(
          color: UnibosColors.bgDark,
          borderRadius: BorderRadius.circular(12),
        ),
        child: Text(
          message.decryptedContent ?? 'system message',
          style: Theme.of(context).textTheme.bodySmall?.copyWith(
                color: UnibosColors.textMuted,
              ),
        ),
      ),
    );
  }

  void _showMessageOptions(BuildContext context) {
    showModalBottomSheet(
      context: context,
      builder: (context) => Container(
        padding: const EdgeInsets.all(16),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            ListTile(
              leading: const Icon(Icons.reply),
              title: const Text('reply'),
              onTap: () {
                Navigator.pop(context);
                onReply?.call();
              },
            ),
            ListTile(
              leading: const Icon(Icons.emoji_emotions),
              title: const Text('react'),
              onTap: () {
                Navigator.pop(context);
                _showReactionPicker(context);
              },
            ),
            ListTile(
              leading: const Icon(Icons.copy),
              title: const Text('copy'),
              onTap: () {
                Navigator.pop(context);
                // TODO: Copy to clipboard
              },
            ),
            if (isOwnMessage) ...[
              ListTile(
                leading: const Icon(Icons.edit),
                title: const Text('edit'),
                onTap: () {
                  Navigator.pop(context);
                  // TODO: Edit message
                },
              ),
              ListTile(
                leading: const Icon(Icons.delete, color: UnibosColors.red),
                title: const Text('delete', style: TextStyle(color: UnibosColors.red)),
                onTap: () {
                  Navigator.pop(context);
                  // TODO: Delete message
                },
              ),
            ],
          ],
        ),
      ),
    );
  }

  void _showReactionPicker(BuildContext context) {
    final reactions = ['👍', '❤️', '😂', '😮', '😢', '🎉'];

    showModalBottomSheet(
      context: context,
      builder: (context) => Container(
        padding: const EdgeInsets.all(24),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.spaceEvenly,
          children: reactions.map((emoji) {
            return GestureDetector(
              onTap: () {
                Navigator.pop(context);
                onReact?.call(emoji);
              },
              child: Text(emoji, style: const TextStyle(fontSize: 32)),
            );
          }).toList(),
        ),
      ),
    );
  }

  String _formatTime(DateTime time) {
    return '${time.hour.toString().padLeft(2, '0')}:${time.minute.toString().padLeft(2, '0')}';
  }
}
