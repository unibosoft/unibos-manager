/// Message Input Widget
///
/// Text input field with send button and attachment options.

import 'dart:async';
import 'package:flutter/material.dart';
import '../../../core/theme/colors.dart';

class MessageInput extends StatefulWidget {
  final TextEditingController controller;
  final VoidCallback onSend;
  final Function(bool)? onTypingChanged;
  final VoidCallback? onAttachment;

  const MessageInput({
    super.key,
    required this.controller,
    required this.onSend,
    this.onTypingChanged,
    this.onAttachment,
  });

  @override
  State<MessageInput> createState() => _MessageInputState();
}

class _MessageInputState extends State<MessageInput> {
  bool _hasText = false;
  Timer? _typingTimer;

  @override
  void initState() {
    super.initState();
    widget.controller.addListener(_onTextChanged);
  }

  @override
  void dispose() {
    widget.controller.removeListener(_onTextChanged);
    _typingTimer?.cancel();
    super.dispose();
  }

  void _onTextChanged() {
    final hasText = widget.controller.text.isNotEmpty;
    if (hasText != _hasText) {
      setState(() => _hasText = hasText);
    }

    // Handle typing indicator
    if (hasText) {
      // Notify typing started
      widget.onTypingChanged?.call(true);

      // Reset timer
      _typingTimer?.cancel();
      _typingTimer = Timer(const Duration(seconds: 3), () {
        widget.onTypingChanged?.call(false);
      });
    } else {
      _typingTimer?.cancel();
      widget.onTypingChanged?.call(false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 8),
      decoration: BoxDecoration(
        color: UnibosColors.bgBlack,
        border: const Border(
          top: BorderSide(color: UnibosColors.bgDark),
        ),
      ),
      child: SafeArea(
        top: false,
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.end,
          children: [
            // Attachment button
            IconButton(
              icon: const Icon(Icons.add_circle_outline),
              color: UnibosColors.textMuted,
              onPressed: () => _showAttachmentOptions(context),
              padding: const EdgeInsets.all(8),
              constraints: const BoxConstraints(),
            ),

            const SizedBox(width: 4),

            // Text input
            Expanded(
              child: Container(
                constraints: const BoxConstraints(maxHeight: 120),
                decoration: BoxDecoration(
                  color: UnibosColors.bgDark,
                  borderRadius: BorderRadius.circular(20),
                ),
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.end,
                  children: [
                    Expanded(
                      child: TextField(
                        controller: widget.controller,
                        maxLines: null,
                        textInputAction: TextInputAction.newline,
                        decoration: const InputDecoration(
                          hintText: 'message...',
                          hintStyle: TextStyle(color: UnibosColors.textMuted),
                          border: InputBorder.none,
                          contentPadding: EdgeInsets.symmetric(
                            horizontal: 16,
                            vertical: 10,
                          ),
                        ),
                      ),
                    ),
                    // Emoji button
                    IconButton(
                      icon: const Icon(Icons.emoji_emotions_outlined, size: 20),
                      color: UnibosColors.textMuted,
                      onPressed: () {
                        // TODO: Show emoji picker
                      },
                      padding: const EdgeInsets.all(8),
                      constraints: const BoxConstraints(),
                    ),
                  ],
                ),
              ),
            ),

            const SizedBox(width: 4),

            // Send button
            AnimatedContainer(
              duration: const Duration(milliseconds: 200),
              child: _hasText
                  ? IconButton(
                      icon: const Icon(Icons.send),
                      color: UnibosColors.orange,
                      onPressed: () {
                        widget.onSend();
                        _typingTimer?.cancel();
                        widget.onTypingChanged?.call(false);
                      },
                      padding: const EdgeInsets.all(8),
                      constraints: const BoxConstraints(),
                    )
                  : IconButton(
                      icon: const Icon(Icons.mic),
                      color: UnibosColors.textMuted,
                      onPressed: () {
                        // TODO: Voice message
                      },
                      padding: const EdgeInsets.all(8),
                      constraints: const BoxConstraints(),
                    ),
            ),
          ],
        ),
      ),
    );
  }

  void _showAttachmentOptions(BuildContext context) {
    showModalBottomSheet(
      context: context,
      builder: (context) => Container(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceEvenly,
              children: [
                _AttachmentOption(
                  icon: Icons.photo,
                  label: 'photo',
                  color: UnibosColors.green,
                  onTap: () {
                    Navigator.pop(context);
                    // TODO: Pick photo
                  },
                ),
                _AttachmentOption(
                  icon: Icons.camera_alt,
                  label: 'camera',
                  color: UnibosColors.blue,
                  onTap: () {
                    Navigator.pop(context);
                    // TODO: Take photo
                  },
                ),
                _AttachmentOption(
                  icon: Icons.insert_drive_file,
                  label: 'file',
                  color: UnibosColors.orange,
                  onTap: () {
                    Navigator.pop(context);
                    // TODO: Pick file
                  },
                ),
                _AttachmentOption(
                  icon: Icons.location_on,
                  label: 'location',
                  color: UnibosColors.red,
                  onTap: () {
                    Navigator.pop(context);
                    // TODO: Share location
                  },
                ),
              ],
            ),
            const SizedBox(height: 16),
          ],
        ),
      ),
    );
  }
}

class _AttachmentOption extends StatelessWidget {
  final IconData icon;
  final String label;
  final Color color;
  final VoidCallback onTap;

  const _AttachmentOption({
    required this.icon,
    required this.label,
    required this.color,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Container(
            width: 56,
            height: 56,
            decoration: BoxDecoration(
              color: color.withValues(alpha: 0.2),
              shape: BoxShape.circle,
            ),
            child: Icon(icon, color: color),
          ),
          const SizedBox(height: 8),
          Text(
            label,
            style: const TextStyle(fontSize: 12),
          ),
        ],
      ),
    );
  }
}
