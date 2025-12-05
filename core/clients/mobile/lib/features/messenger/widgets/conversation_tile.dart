/// Conversation Tile Widget
///
/// List tile for displaying a conversation in the list.

import 'package:flutter/material.dart';
import '../../../core/theme/colors.dart';
import '../../../core/messenger/messenger_models.dart';

class ConversationTile extends StatelessWidget {
  final Conversation conversation;
  final VoidCallback onTap;

  const ConversationTile({
    super.key,
    required this.conversation,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
        child: Row(
          children: [
            // Avatar
            _buildAvatar(),
            const SizedBox(width: 12),

            // Content
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Title row
                  Row(
                    children: [
                      Expanded(
                        child: Text(
                          conversation.displayName,
                          style: TextStyle(
                            fontSize: 15,
                            fontWeight: conversation.unreadCount > 0
                                ? FontWeight.bold
                                : FontWeight.normal,
                          ),
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis,
                        ),
                      ),
                      if (conversation.lastMessageAt != null)
                        Text(
                          _formatTime(conversation.lastMessageAt!),
                          style: TextStyle(
                            fontSize: 12,
                            color: conversation.unreadCount > 0
                                ? UnibosColors.orange
                                : UnibosColors.textMuted,
                          ),
                        ),
                    ],
                  ),
                  const SizedBox(height: 4),

                  // Last message preview
                  Row(
                    children: [
                      // Encryption indicator
                      if (conversation.isEncrypted)
                        const Padding(
                          padding: EdgeInsets.only(right: 4),
                          child: Icon(
                            Icons.lock,
                            size: 12,
                            color: UnibosColors.green,
                          ),
                        ),

                      // P2P indicator
                      if (conversation.p2pEnabled)
                        const Padding(
                          padding: EdgeInsets.only(right: 4),
                          child: Icon(
                            Icons.wifi_tethering,
                            size: 12,
                            color: UnibosColors.orange,
                          ),
                        ),

                      // Message preview
                      Expanded(
                        child: Text(
                          _getLastMessagePreview(),
                          style: TextStyle(
                            fontSize: 13,
                            color: conversation.unreadCount > 0
                                ? UnibosColors.textMain
                                : UnibosColors.textMuted,
                          ),
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis,
                        ),
                      ),

                      // Unread badge
                      if (conversation.unreadCount > 0)
                        Container(
                          margin: const EdgeInsets.only(left: 8),
                          padding: const EdgeInsets.symmetric(
                            horizontal: 6,
                            vertical: 2,
                          ),
                          decoration: BoxDecoration(
                            color: UnibosColors.orange,
                            borderRadius: BorderRadius.circular(10),
                          ),
                          child: Text(
                            conversation.unreadCount > 99
                                ? '99+'
                                : conversation.unreadCount.toString(),
                            style: const TextStyle(
                              fontSize: 11,
                              color: Colors.white,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        ),
                    ],
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildAvatar() {
    return Stack(
      children: [
        CircleAvatar(
          radius: 24,
          backgroundColor: UnibosColors.orange,
          backgroundImage: conversation.avatar != null
              ? NetworkImage(conversation.avatar!)
              : null,
          child: conversation.avatar == null
              ? Text(
                  _getInitials(),
                  style: const TextStyle(
                    color: Colors.white,
                    fontWeight: FontWeight.bold,
                  ),
                )
              : null,
        ),
        // Group indicator
        if (conversation.isGroup)
          Positioned(
            right: 0,
            bottom: 0,
            child: Container(
              padding: const EdgeInsets.all(2),
              decoration: BoxDecoration(
                color: UnibosColors.bgBlack,
                shape: BoxShape.circle,
                border: Border.all(color: UnibosColors.bgDark, width: 1),
              ),
              child: const Icon(
                Icons.group,
                size: 10,
                color: UnibosColors.textMuted,
              ),
            ),
          ),
      ],
    );
  }

  String _getInitials() {
    final name = conversation.displayName;
    if (name.isEmpty) return '?';

    final parts = name.split(' ');
    if (parts.length >= 2) {
      return '${parts[0][0]}${parts[1][0]}'.toUpperCase();
    }
    return name[0].toUpperCase();
  }

  String _getLastMessagePreview() {
    final lastMessage = conversation.lastMessage;
    if (lastMessage == null) {
      return 'no messages yet';
    }

    if (lastMessage.isDeleted) {
      return 'message deleted';
    }

    switch (lastMessage.messageType) {
      case 'text':
        return 'encrypted message';
      case 'image':
        return 'sent an image';
      case 'file':
        return 'sent a file';
      case 'voice':
        return 'sent a voice message';
      case 'video':
        return 'sent a video';
      case 'system':
        return 'system message';
      default:
        return 'new message';
    }
  }

  String _formatTime(DateTime time) {
    final now = DateTime.now();
    final diff = now.difference(time);

    if (diff.inDays == 0) {
      // Today - show time
      return '${time.hour.toString().padLeft(2, '0')}:${time.minute.toString().padLeft(2, '0')}';
    } else if (diff.inDays == 1) {
      return 'yesterday';
    } else if (diff.inDays < 7) {
      const days = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun'];
      return days[time.weekday - 1];
    } else {
      return '${time.day}/${time.month}';
    }
  }
}
