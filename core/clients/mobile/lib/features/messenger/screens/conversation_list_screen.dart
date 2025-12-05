/// Conversation List Screen
///
/// Main messenger screen showing list of conversations.

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../core/theme/colors.dart';
import '../../../core/messenger/messenger_models.dart';
import '../providers/messenger_provider.dart';
import '../widgets/conversation_tile.dart';

class ConversationListScreen extends ConsumerWidget {
  const ConversationListScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final conversationsAsync = ref.watch(conversationsProvider);
    final transportMode = ref.watch(transportModeProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('messenger'),
        actions: [
          // Transport mode indicator
          Padding(
            padding: const EdgeInsets.only(right: 8),
            child: IconButton(
              icon: Icon(
                transportMode == TransportMode.p2p
                    ? Icons.wifi_tethering
                    : transportMode == TransportMode.hybrid
                        ? Icons.compare_arrows
                        : Icons.cloud,
                size: 20,
              ),
              onPressed: () => _showTransportSettings(context, ref),
              tooltip: 'Transport: ${transportMode.name}',
            ),
          ),
          // New conversation button
          IconButton(
            icon: const Icon(Icons.edit_square, size: 20),
            onPressed: () => context.push('/messenger/new'),
            tooltip: 'new conversation',
          ),
        ],
      ),
      body: conversationsAsync.when(
        data: (conversations) {
          if (conversations.isEmpty) {
            return _buildEmptyState(context);
          }
          return RefreshIndicator(
            onRefresh: () async {
              ref.invalidate(conversationsProvider);
            },
            color: UnibosColors.orange,
            child: ListView.builder(
              itemCount: conversations.length,
              itemBuilder: (context, index) {
                final conversation = conversations[index];
                return ConversationTile(
                  conversation: conversation,
                  onTap: () => context.push('/messenger/chat/${conversation.id}'),
                );
              },
            ),
          );
        },
        loading: () => const Center(
          child: CircularProgressIndicator(),
        ),
        error: (error, stack) => Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Icon(Icons.error_outline, size: 48, color: UnibosColors.red),
              const SizedBox(height: 16),
              Text(
                'failed to load conversations',
                style: Theme.of(context).textTheme.bodyLarge,
              ),
              const SizedBox(height: 8),
              TextButton(
                onPressed: () => ref.invalidate(conversationsProvider),
                child: const Text('retry'),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildEmptyState(BuildContext context) {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const Icon(
            Icons.chat_bubble_outline,
            size: 64,
            color: UnibosColors.textMuted,
          ),
          const SizedBox(height: 16),
          Text(
            'no conversations yet',
            style: Theme.of(context).textTheme.titleMedium?.copyWith(
                  color: UnibosColors.textMuted,
                ),
          ),
          const SizedBox(height: 8),
          Text(
            'start a new conversation to begin messaging',
            style: Theme.of(context).textTheme.bodySmall?.copyWith(
                  color: UnibosColors.textMuted,
                ),
          ),
          const SizedBox(height: 24),
          ElevatedButton.icon(
            onPressed: () => context.push('/messenger/new'),
            icon: const Icon(Icons.add),
            label: const Text('new conversation'),
          ),
        ],
      ),
    );
  }

  void _showTransportSettings(BuildContext context, WidgetRef ref) {
    showModalBottomSheet(
      context: context,
      builder: (context) => Container(
        padding: const EdgeInsets.all(16),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'transport mode',
              style: Theme.of(context).textTheme.titleMedium,
            ),
            const SizedBox(height: 8),
            Text(
              'choose how messages are delivered',
              style: Theme.of(context).textTheme.bodySmall?.copyWith(
                    color: UnibosColors.textMuted,
                  ),
            ),
            const SizedBox(height: 16),
            ListTile(
              leading: const Icon(Icons.cloud),
              title: const Text('hub relay'),
              subtitle: const Text('messages routed through server'),
              selected: ref.read(transportModeProvider) == TransportMode.hub,
              onTap: () {
                ref.read(transportModeProvider.notifier).state = TransportMode.hub;
                Navigator.pop(context);
              },
            ),
            ListTile(
              leading: const Icon(Icons.wifi_tethering),
              title: const Text('p2p direct'),
              subtitle: const Text('direct peer-to-peer connection'),
              selected: ref.read(transportModeProvider) == TransportMode.p2p,
              onTap: () {
                ref.read(transportModeProvider.notifier).state = TransportMode.p2p;
                Navigator.pop(context);
              },
            ),
            ListTile(
              leading: const Icon(Icons.compare_arrows),
              title: const Text('hybrid'),
              subtitle: const Text('p2p when available, hub fallback'),
              selected: ref.read(transportModeProvider) == TransportMode.hybrid,
              onTap: () {
                ref.read(transportModeProvider.notifier).state = TransportMode.hybrid;
                Navigator.pop(context);
              },
            ),
            const SizedBox(height: 16),
          ],
        ),
      ),
    );
  }
}
