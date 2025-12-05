/// New Conversation Screen
///
/// Create a new direct or group conversation.

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../core/theme/colors.dart';
import '../providers/messenger_provider.dart';

class NewConversationScreen extends ConsumerStatefulWidget {
  const NewConversationScreen({super.key});

  @override
  ConsumerState<NewConversationScreen> createState() => _NewConversationScreenState();
}

class _NewConversationScreenState extends ConsumerState<NewConversationScreen> {
  final TextEditingController _searchController = TextEditingController();
  final List<String> _selectedUserIds = [];
  bool _isGroup = false;
  String? _groupName;
  bool _isLoading = false;
  bool _enableP2P = false;

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        leading: IconButton(
          icon: const Icon(Icons.close),
          onPressed: () => context.pop(),
        ),
        title: Text(_isGroup ? 'new group' : 'new conversation'),
        actions: [
          if (_selectedUserIds.isNotEmpty)
            TextButton(
              onPressed: _isLoading ? null : _createConversation,
              child: _isLoading
                  ? const SizedBox(
                      width: 16,
                      height: 16,
                      child: CircularProgressIndicator(strokeWidth: 2),
                    )
                  : const Text('create'),
            ),
        ],
      ),
      body: Column(
        children: [
          // Conversation type toggle
          _buildTypeToggle(),

          // Group name input (if group)
          if (_isGroup) _buildGroupNameInput(),

          // P2P toggle
          _buildP2PToggle(),

          // Search input
          _buildSearchInput(),

          // User list
          Expanded(
            child: _buildUserList(),
          ),

          // Selected users chips
          if (_selectedUserIds.isNotEmpty) _buildSelectedUsers(),
        ],
      ),
    );
  }

  Widget _buildTypeToggle() {
    return Container(
      padding: const EdgeInsets.all(16),
      child: Row(
        children: [
          Expanded(
            child: _TypeButton(
              icon: Icons.person,
              label: 'direct',
              isSelected: !_isGroup,
              onTap: () => setState(() => _isGroup = false),
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: _TypeButton(
              icon: Icons.group,
              label: 'group',
              isSelected: _isGroup,
              onTap: () => setState(() => _isGroup = true),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildGroupNameInput() {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      child: TextField(
        decoration: InputDecoration(
          hintText: 'group name',
          prefixIcon: const Icon(Icons.group),
          border: OutlineInputBorder(
            borderRadius: BorderRadius.circular(8),
          ),
        ),
        onChanged: (value) => _groupName = value,
      ),
    );
  }

  Widget _buildP2PToggle() {
    return SwitchListTile(
      title: const Text('enable p2p'),
      subtitle: Text(
        _enableP2P
            ? 'messages can be sent directly between devices'
            : 'messages will be routed through the server',
        style: Theme.of(context).textTheme.bodySmall?.copyWith(
              color: UnibosColors.textMuted,
            ),
      ),
      secondary: Icon(
        _enableP2P ? Icons.wifi_tethering : Icons.cloud,
        color: _enableP2P ? UnibosColors.orange : UnibosColors.textMuted,
      ),
      value: _enableP2P,
      onChanged: (value) => setState(() => _enableP2P = value),
    );
  }

  Widget _buildSearchInput() {
    return Padding(
      padding: const EdgeInsets.all(16),
      child: TextField(
        controller: _searchController,
        decoration: InputDecoration(
          hintText: 'search users...',
          prefixIcon: const Icon(Icons.search),
          border: OutlineInputBorder(
            borderRadius: BorderRadius.circular(8),
          ),
        ),
        onChanged: (value) {
          // TODO: Implement user search
          setState(() {});
        },
      ),
    );
  }

  Widget _buildUserList() {
    // TODO: Implement actual user search from API
    // For now, show placeholder
    final searchQuery = _searchController.text.toLowerCase();

    if (searchQuery.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(
              Icons.search,
              size: 48,
              color: UnibosColors.textMuted,
            ),
            const SizedBox(height: 16),
            Text(
              'search for users to start a conversation',
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    color: UnibosColors.textMuted,
                  ),
            ),
          ],
        ),
      );
    }

    // Placeholder users for demo
    final demoUsers = [
      {'id': 'user1', 'name': 'Alice', 'username': 'alice'},
      {'id': 'user2', 'name': 'Bob', 'username': 'bob'},
      {'id': 'user3', 'name': 'Charlie', 'username': 'charlie'},
    ].where((user) =>
        user['name']!.toLowerCase().contains(searchQuery) ||
        user['username']!.toLowerCase().contains(searchQuery));

    return ListView.builder(
      itemCount: demoUsers.length,
      itemBuilder: (context, index) {
        final user = demoUsers.elementAt(index);
        final isSelected = _selectedUserIds.contains(user['id']);

        return ListTile(
          leading: CircleAvatar(
            backgroundColor: UnibosColors.orange,
            child: Text(
              user['name']![0].toUpperCase(),
              style: const TextStyle(color: Colors.white),
            ),
          ),
          title: Text(user['name']!),
          subtitle: Text('@${user['username']}'),
          trailing: isSelected
              ? const Icon(Icons.check_circle, color: UnibosColors.green)
              : const Icon(Icons.radio_button_unchecked),
          onTap: () {
            setState(() {
              if (isSelected) {
                _selectedUserIds.remove(user['id']);
              } else {
                if (!_isGroup) {
                  _selectedUserIds.clear();
                }
                _selectedUserIds.add(user['id']!);
              }
            });
          },
        );
      },
    );
  }

  Widget _buildSelectedUsers() {
    return Container(
      padding: const EdgeInsets.all(8),
      decoration: BoxDecoration(
        color: UnibosColors.bgBlack.withValues(alpha: 0.3),
        border: const Border(
          top: BorderSide(color: UnibosColors.bgDark),
        ),
      ),
      child: Wrap(
        spacing: 8,
        runSpacing: 8,
        children: _selectedUserIds.map((userId) {
          return Chip(
            label: Text(userId),
            onDeleted: () {
              setState(() {
                _selectedUserIds.remove(userId);
              });
            },
          );
        }).toList(),
      ),
    );
  }

  Future<void> _createConversation() async {
    if (_selectedUserIds.isEmpty) return;
    if (_isGroup && (_groupName == null || _groupName!.isEmpty)) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('please enter a group name')),
      );
      return;
    }

    setState(() => _isLoading = true);

    try {
      final service = ref.read(messengerServiceProvider);
      final conversation = await service.createConversation(
        participantIds: _selectedUserIds,
        type: _isGroup ? 'group' : 'direct',
        name: _groupName,
        p2pEnabled: _enableP2P,
        transportMode: _enableP2P ? 'hybrid' : 'hub',
      );

      if (mounted) {
        ref.invalidate(conversationsProvider);
        context.go('/messenger/chat/${conversation.id}');
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('failed to create conversation: $e')),
        );
      }
    } finally {
      if (mounted) {
        setState(() => _isLoading = false);
      }
    }
  }
}

class _TypeButton extends StatelessWidget {
  final IconData icon;
  final String label;
  final bool isSelected;
  final VoidCallback onTap;

  const _TypeButton({
    required this.icon,
    required this.label,
    required this.isSelected,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(8),
      child: Container(
        padding: const EdgeInsets.symmetric(vertical: 12),
        decoration: BoxDecoration(
          color: isSelected
              ? UnibosColors.orange.withValues(alpha: 0.2)
              : Colors.transparent,
          border: Border.all(
            color: isSelected ? UnibosColors.orange : UnibosColors.bgDark,
          ),
          borderRadius: BorderRadius.circular(8),
        ),
        child: Column(
          children: [
            Icon(
              icon,
              color: isSelected ? UnibosColors.orange : UnibosColors.textMuted,
            ),
            const SizedBox(height: 4),
            Text(
              label,
              style: TextStyle(
                color: isSelected ? UnibosColors.orange : UnibosColors.textMuted,
                fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
              ),
            ),
          ],
        ),
      ),
    );
  }
}
