import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/sync/sync.dart';

/// sync status screen
class SyncScreen extends ConsumerStatefulWidget {
  const SyncScreen({super.key});

  @override
  ConsumerState<SyncScreen> createState() => _SyncScreenState();
}

class _SyncScreenState extends ConsumerState<SyncScreen> {
  @override
  void initState() {
    super.initState();
    _loadSyncStatus();
  }

  Future<void> _loadSyncStatus() async {
    final syncService = ref.read(syncServiceProvider);
    await syncService.getSyncStatus();
  }

  Future<void> _performSync() async {
    final syncService = ref.read(syncServiceProvider);
    await syncService.performSync();
  }

  @override
  Widget build(BuildContext context) {
    final syncState = ref.watch(syncStateProvider);
    final theme = Theme.of(context);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Sync'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: syncState.isSyncing ? null : _loadSyncStatus,
          ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: _loadSyncStatus,
        child: ListView(
          padding: const EdgeInsets.all(16),
          children: [
            // Sync Status Card
            _buildStatusCard(syncState, theme),

            const SizedBox(height: 16),

            // Pending Changes Card
            _buildPendingCard(syncState, theme),

            const SizedBox(height: 16),

            // Conflicts Card
            if (syncState.unresolvedConflicts > 0)
              _buildConflictsCard(syncState, theme),

            const SizedBox(height: 24),

            // Sync Button
            SizedBox(
              width: double.infinity,
              height: 48,
              child: ElevatedButton.icon(
                onPressed: syncState.isSyncing ? null : _performSync,
                icon: syncState.isSyncing
                    ? const SizedBox(
                        width: 20,
                        height: 20,
                        child: CircularProgressIndicator(strokeWidth: 2),
                      )
                    : const Icon(Icons.sync),
                label: Text(syncState.isSyncing ? 'Syncing...' : 'Sync Now'),
              ),
            ),

            if (syncState.isSyncing) ...[
              const SizedBox(height: 16),
              LinearProgressIndicator(value: syncState.progress),
              const SizedBox(height: 8),
              Text(
                '${(syncState.progress * 100).toInt()}%',
                textAlign: TextAlign.center,
                style: theme.textTheme.bodySmall,
              ),
            ],

            if (syncState.errorMessage != null) ...[
              const SizedBox(height: 16),
              Card(
                color: theme.colorScheme.errorContainer,
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Row(
                    children: [
                      Icon(
                        Icons.error_outline,
                        color: theme.colorScheme.onErrorContainer,
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: Text(
                          syncState.errorMessage!,
                          style: TextStyle(
                            color: theme.colorScheme.onErrorContainer,
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildStatusCard(SyncState state, ThemeData theme) {
    IconData statusIcon;
    Color statusColor;
    String statusText;

    switch (state.status) {
      case SyncStatus.completed:
        statusIcon = Icons.check_circle;
        statusColor = Colors.green;
        statusText = 'Synced';
        break;
      case SyncStatus.inProgress:
        statusIcon = Icons.sync;
        statusColor = Colors.blue;
        statusText = 'Syncing';
        break;
      case SyncStatus.conflict:
        statusIcon = Icons.warning;
        statusColor = Colors.orange;
        statusText = 'Conflicts';
        break;
      case SyncStatus.failed:
        statusIcon = Icons.error;
        statusColor = Colors.red;
        statusText = 'Failed';
        break;
      default:
        statusIcon = Icons.cloud_off;
        statusColor = Colors.grey;
        statusText = 'Not Synced';
    }

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(statusIcon, color: statusColor, size: 32),
                const SizedBox(width: 12),
                Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Sync Status',
                      style: theme.textTheme.titleMedium,
                    ),
                    Text(
                      statusText,
                      style: theme.textTheme.bodyLarge?.copyWith(
                        color: statusColor,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ],
                ),
              ],
            ),
            if (state.lastSyncTime != null) ...[
              const Divider(height: 24),
              Text(
                'Last Sync',
                style: theme.textTheme.bodySmall?.copyWith(
                  color: theme.colorScheme.outline,
                ),
              ),
              const SizedBox(height: 4),
              Text(
                _formatDateTime(state.lastSyncTime!),
                style: theme.textTheme.bodyMedium,
              ),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildPendingCard(SyncState state, ThemeData theme) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Row(
          children: [
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: theme.colorScheme.primaryContainer,
                borderRadius: BorderRadius.circular(12),
              ),
              child: Icon(
                Icons.upload,
                color: theme.colorScheme.onPrimaryContainer,
              ),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Pending Changes',
                    style: theme.textTheme.titleSmall,
                  ),
                  Text(
                    '${state.pendingChanges} items waiting to sync',
                    style: theme.textTheme.bodyMedium?.copyWith(
                      color: theme.colorScheme.outline,
                    ),
                  ),
                ],
              ),
            ),
            Text(
              '${state.pendingChanges}',
              style: theme.textTheme.headlineMedium?.copyWith(
                fontWeight: FontWeight.bold,
                color: theme.colorScheme.primary,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildConflictsCard(SyncState state, ThemeData theme) {
    return Card(
      color: theme.colorScheme.errorContainer.withAlpha(50),
      child: InkWell(
        onTap: () => _showConflictsDialog(),
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Row(
            children: [
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: theme.colorScheme.errorContainer,
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Icon(
                  Icons.warning_amber,
                  color: theme.colorScheme.onErrorContainer,
                ),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Conflicts Detected',
                      style: theme.textTheme.titleSmall?.copyWith(
                        color: theme.colorScheme.error,
                      ),
                    ),
                    Text(
                      '${state.unresolvedConflicts} conflicts need resolution',
                      style: theme.textTheme.bodyMedium?.copyWith(
                        color: theme.colorScheme.outline,
                      ),
                    ),
                  ],
                ),
              ),
              Icon(
                Icons.chevron_right,
                color: theme.colorScheme.error,
              ),
            ],
          ),
        ),
      ),
    );
  }

  void _showConflictsDialog() {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => const ConflictResolutionScreen(),
      ),
    );
  }

  String _formatDateTime(DateTime dt) {
    final now = DateTime.now();
    final diff = now.difference(dt);

    if (diff.inMinutes < 1) {
      return 'Just now';
    } else if (diff.inHours < 1) {
      return '${diff.inMinutes} minutes ago';
    } else if (diff.inDays < 1) {
      return '${diff.inHours} hours ago';
    } else {
      return '${diff.inDays} days ago';
    }
  }
}

/// conflict resolution screen
class ConflictResolutionScreen extends ConsumerStatefulWidget {
  const ConflictResolutionScreen({super.key});

  @override
  ConsumerState<ConflictResolutionScreen> createState() =>
      _ConflictResolutionScreenState();
}

class _ConflictResolutionScreenState
    extends ConsumerState<ConflictResolutionScreen> {
  List<SyncConflict> _conflicts = [];
  bool _loading = true;

  @override
  void initState() {
    super.initState();
    _loadConflicts();
  }

  Future<void> _loadConflicts() async {
    setState(() => _loading = true);
    final syncService = ref.read(syncServiceProvider);
    final conflicts = await syncService.getConflicts();
    setState(() {
      _conflicts = conflicts;
      _loading = false;
    });
  }

  Future<void> _resolveConflict(
    SyncConflict conflict,
    ConflictStrategy strategy,
  ) async {
    final syncService = ref.read(syncServiceProvider);
    final success = await syncService.resolveConflict(conflict.id, strategy);

    if (success && mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Conflict resolved')),
      );
      _loadConflicts();
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Resolve Conflicts'),
      ),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : _conflicts.isEmpty
              ? Center(
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Icon(
                        Icons.check_circle_outline,
                        size: 64,
                        color: theme.colorScheme.primary,
                      ),
                      const SizedBox(height: 16),
                      Text(
                        'No conflicts',
                        style: theme.textTheme.titleLarge,
                      ),
                      Text(
                        'All data is in sync',
                        style: theme.textTheme.bodyMedium?.copyWith(
                          color: theme.colorScheme.outline,
                        ),
                      ),
                    ],
                  ),
                )
              : ListView.builder(
                  padding: const EdgeInsets.all(16),
                  itemCount: _conflicts.length,
                  itemBuilder: (context, index) {
                    final conflict = _conflicts[index];
                    return _buildConflictCard(conflict, theme);
                  },
                ),
    );
  }

  Widget _buildConflictCard(SyncConflict conflict, ThemeData theme) {
    return Card(
      margin: const EdgeInsets.only(bottom: 16),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(
                  Icons.warning_amber,
                  color: theme.colorScheme.error,
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    '${conflict.modelName} - ${conflict.recordId}',
                    style: theme.textTheme.titleMedium,
                  ),
                ),
              ],
            ),
            const Divider(height: 24),

            // Local vs Remote comparison
            Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Expanded(
                  child: _buildDataColumn(
                    'Local (Device)',
                    conflict.localData,
                    conflict.localModifiedAt,
                    theme,
                    Colors.blue,
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: _buildDataColumn(
                    'Remote (Hub)',
                    conflict.remoteData,
                    conflict.remoteModifiedAt,
                    theme,
                    Colors.green,
                  ),
                ),
              ],
            ),

            const Divider(height: 24),

            // Resolution buttons
            Text(
              'Resolution',
              style: theme.textTheme.titleSmall,
            ),
            const SizedBox(height: 12),
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: [
                OutlinedButton.icon(
                  onPressed: () => _resolveConflict(
                    conflict,
                    ConflictStrategy.nodeWins,
                  ),
                  icon: const Icon(Icons.smartphone, size: 18),
                  label: const Text('Keep Local'),
                ),
                OutlinedButton.icon(
                  onPressed: () => _resolveConflict(
                    conflict,
                    ConflictStrategy.hubWins,
                  ),
                  icon: const Icon(Icons.cloud, size: 18),
                  label: const Text('Keep Remote'),
                ),
                OutlinedButton.icon(
                  onPressed: () => _resolveConflict(
                    conflict,
                    ConflictStrategy.newerWins,
                  ),
                  icon: const Icon(Icons.schedule, size: 18),
                  label: const Text('Keep Newer'),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildDataColumn(
    String title,
    Map<String, dynamic> data,
    DateTime modifiedAt,
    ThemeData theme,
    Color color,
  ) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
          decoration: BoxDecoration(
            color: color.withAlpha(30),
            borderRadius: BorderRadius.circular(4),
          ),
          child: Text(
            title,
            style: theme.textTheme.labelMedium?.copyWith(
              color: color,
              fontWeight: FontWeight.bold,
            ),
          ),
        ),
        const SizedBox(height: 8),
        Text(
          _formatDateTime(modifiedAt),
          style: theme.textTheme.bodySmall?.copyWith(
            color: theme.colorScheme.outline,
          ),
        ),
        const SizedBox(height: 8),
        Container(
          padding: const EdgeInsets.all(8),
          decoration: BoxDecoration(
            color: theme.colorScheme.surfaceContainerHighest,
            borderRadius: BorderRadius.circular(8),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: data.entries.take(5).map((e) {
              return Padding(
                padding: const EdgeInsets.symmetric(vertical: 2),
                child: Text(
                  '${e.key}: ${e.value}',
                  style: theme.textTheme.bodySmall,
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                ),
              );
            }).toList(),
          ),
        ),
      ],
    );
  }

  String _formatDateTime(DateTime dt) {
    return '${dt.day}/${dt.month}/${dt.year} ${dt.hour}:${dt.minute.toString().padLeft(2, '0')}';
  }
}
