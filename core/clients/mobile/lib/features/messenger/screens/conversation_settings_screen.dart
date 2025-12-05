/// Conversation Settings Screen
///
/// View and manage conversation settings, participants, encryption.

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../core/theme/colors.dart';
import '../../../core/messenger/messenger_models.dart';
import '../providers/messenger_provider.dart';

class ConversationSettingsScreen extends ConsumerWidget {
  final String conversationId;

  const ConversationSettingsScreen({super.key, required this.conversationId});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final conversationAsync = ref.watch(conversationProvider(conversationId));

    return Scaffold(
      appBar: AppBar(
        title: const Text('conversation settings'),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () => context.pop(),
        ),
      ),
      body: conversationAsync.when(
        data: (conversation) => _buildContent(context, ref, conversation),
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (error, stack) => Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Icon(Icons.error_outline, size: 48, color: UnibosColors.red),
              const SizedBox(height: 16),
              const Text('failed to load conversation'),
              TextButton(
                onPressed: () => ref.invalidate(conversationProvider(conversationId)),
                child: const Text('retry'),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildContent(BuildContext context, WidgetRef ref, Conversation conversation) {
    return ListView(
      children: [
        // Conversation Info
        _buildHeader(context, conversation),

        const Divider(),

        // Encryption Status
        _buildEncryptionSection(context, conversation),

        const Divider(),

        // Transport Mode
        _buildTransportSection(context, ref, conversation),

        const Divider(),

        // Participants
        _buildParticipantsSection(context, conversation),

        const Divider(),

        // Actions
        _buildActionsSection(context, ref, conversation),
      ],
    );
  }

  Widget _buildHeader(BuildContext context, Conversation conversation) {
    return Padding(
      padding: const EdgeInsets.all(16),
      child: Column(
        children: [
          CircleAvatar(
            radius: 40,
            backgroundColor: UnibosColors.orange,
            child: Text(
              conversation.displayName[0].toUpperCase(),
              style: const TextStyle(fontSize: 32, color: Colors.white),
            ),
          ),
          const SizedBox(height: 12),
          Text(
            conversation.displayName,
            style: Theme.of(context).textTheme.titleLarge,
          ),
          const SizedBox(height: 4),
          Text(
            conversation.isGroup ? 'group chat' : 'direct message',
            style: Theme.of(context).textTheme.bodySmall?.copyWith(
                  color: UnibosColors.textMuted,
                ),
          ),
          if (conversation.description != null) ...[
            const SizedBox(height: 8),
            Text(
              conversation.description!,
              style: Theme.of(context).textTheme.bodyMedium,
              textAlign: TextAlign.center,
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildEncryptionSection(BuildContext context, Conversation conversation) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Padding(
          padding: const EdgeInsets.fromLTRB(16, 16, 16, 8),
          child: Text(
            'encryption',
            style: Theme.of(context).textTheme.titleSmall?.copyWith(
                  color: UnibosColors.textMuted,
                ),
          ),
        ),
        ListTile(
          leading: Icon(
            conversation.isEncrypted ? Icons.lock : Icons.lock_open,
            color: conversation.isEncrypted ? UnibosColors.green : UnibosColors.red,
          ),
          title: Text(conversation.isEncrypted ? 'end-to-end encrypted' : 'not encrypted'),
          subtitle: Text(
            conversation.isEncrypted
                ? 'messages are encrypted on your device'
                : 'messages are not encrypted',
          ),
        ),
        if (conversation.isEncrypted)
          ListTile(
            leading: const Icon(Icons.vpn_key),
            title: const Text('encryption version'),
            subtitle: Text('v${conversation.encryptionVersion}'),
          ),
        if (conversation.isGroup && conversation.isEncrypted)
          ListTile(
            leading: const Icon(Icons.key),
            title: const Text('group key version'),
            subtitle: Text('v${conversation.groupKeyVersion}'),
            trailing: TextButton(
              onPressed: () {
                // TODO: Implement group key rotation
              },
              child: const Text('rotate'),
            ),
          ),
      ],
    );
  }

  Widget _buildTransportSection(BuildContext context, WidgetRef ref, Conversation conversation) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Padding(
          padding: const EdgeInsets.fromLTRB(16, 16, 16, 8),
          child: Text(
            'transport',
            style: Theme.of(context).textTheme.titleSmall?.copyWith(
                  color: UnibosColors.textMuted,
                ),
          ),
        ),
        ListTile(
          leading: Icon(
            conversation.p2pEnabled ? Icons.wifi_tethering : Icons.cloud,
            color: conversation.p2pEnabled ? UnibosColors.orange : UnibosColors.textMuted,
          ),
          title: Text(conversation.transportMode),
          subtitle: Text(
            conversation.p2pEnabled
                ? 'p2p enabled - messages can be sent directly'
                : 'hub only - messages routed through server',
          ),
        ),
        SwitchListTile(
          title: const Text('prefer p2p'),
          subtitle: const Text('use direct connection when available'),
          value: conversation.p2pEnabled,
          onChanged: (value) async {
            try {
              final service = ref.read(messengerServiceProvider);
              await service.updateConversation(
                conversation.id,
                p2pEnabled: value,
                transportMode: value ? 'hybrid' : 'hub',
              );
              ref.invalidate(conversationProvider(conversation.id));
            } catch (e) {
              if (context.mounted) {
                ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(content: Text('failed to update: $e')),
                );
              }
            }
          },
        ),
      ],
    );
  }

  Widget _buildParticipantsSection(BuildContext context, Conversation conversation) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Padding(
          padding: const EdgeInsets.fromLTRB(16, 16, 16, 8),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                'participants (${conversation.participants.length})',
                style: Theme.of(context).textTheme.titleSmall?.copyWith(
                      color: UnibosColors.textMuted,
                    ),
              ),
              if (conversation.isGroup)
                TextButton.icon(
                  onPressed: () {
                    // TODO: Add participant dialog
                  },
                  icon: const Icon(Icons.add, size: 16),
                  label: const Text('add'),
                ),
            ],
          ),
        ),
        ...conversation.participants.map((participant) => ListTile(
              leading: CircleAvatar(
                backgroundColor: UnibosColors.orange,
                child: Text(
                  participant.user?.initials ?? '?',
                  style: const TextStyle(color: Colors.white, fontSize: 12),
                ),
              ),
              title: Text(participant.user?.displayName ?? 'Unknown'),
              subtitle: Text('@${participant.user?.username ?? 'unknown'}'),
              trailing: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  if (participant.isOwner)
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                      decoration: BoxDecoration(
                        color: UnibosColors.orange.withValues(alpha: 0.2),
                        borderRadius: BorderRadius.circular(4),
                      ),
                      child: const Text(
                        'owner',
                        style: TextStyle(fontSize: 10, color: UnibosColors.orange),
                      ),
                    )
                  else if (participant.isAdmin)
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                      decoration: BoxDecoration(
                        color: UnibosColors.blue.withValues(alpha: 0.2),
                        borderRadius: BorderRadius.circular(4),
                      ),
                      child: const Text(
                        'admin',
                        style: TextStyle(fontSize: 10, color: UnibosColors.blue),
                      ),
                    ),
                  if (participant.p2pPreferred)
                    const Padding(
                      padding: EdgeInsets.only(left: 8),
                      child: Icon(
                        Icons.wifi_tethering,
                        size: 16,
                        color: UnibosColors.orange,
                      ),
                    ),
                ],
              ),
            )),
      ],
    );
  }

  Widget _buildActionsSection(BuildContext context, WidgetRef ref, Conversation conversation) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Padding(
          padding: const EdgeInsets.fromLTRB(16, 16, 16, 8),
          child: Text(
            'actions',
            style: Theme.of(context).textTheme.titleSmall?.copyWith(
                  color: UnibosColors.textMuted,
                ),
          ),
        ),
        ListTile(
          leading: const Icon(Icons.notifications_off),
          title: const Text('mute notifications'),
          trailing: Switch(
            value: false, // TODO: Implement notification muting
            onChanged: (value) {},
          ),
        ),
        ListTile(
          leading: const Icon(Icons.search),
          title: const Text('search in conversation'),
          onTap: () {
            // TODO: Implement search
          },
        ),
        ListTile(
          leading: const Icon(Icons.photo_library),
          title: const Text('media & files'),
          onTap: () {
            // TODO: Show media gallery
          },
        ),
        const Divider(),
        ListTile(
          leading: const Icon(Icons.exit_to_app, color: UnibosColors.red),
          title: const Text(
            'leave conversation',
            style: TextStyle(color: UnibosColors.red),
          ),
          onTap: () => _confirmLeave(context, ref, conversation),
        ),
      ],
    );
  }

  void _confirmLeave(BuildContext context, WidgetRef ref, Conversation conversation) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('leave conversation?'),
        content: Text(
          conversation.isGroup
              ? 'you will no longer receive messages from this group.'
              : 'this will delete the conversation.',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('cancel'),
          ),
          TextButton(
            onPressed: () async {
              Navigator.pop(context);
              try {
                final service = ref.read(messengerServiceProvider);
                await service.leaveConversation(conversation.id);
                ref.invalidate(conversationsProvider);
                if (context.mounted) {
                  context.go('/messenger');
                }
              } catch (e) {
                if (context.mounted) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(content: Text('failed to leave: $e')),
                  );
                }
              }
            },
            child: const Text('leave', style: TextStyle(color: UnibosColors.red)),
          ),
        ],
      ),
    );
  }
}
