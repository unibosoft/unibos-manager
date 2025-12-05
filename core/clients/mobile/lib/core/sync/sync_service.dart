import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../api/api_client.dart';
import '../api/endpoints.dart';
import 'sync_models.dart';
import 'offline_queue.dart';

/// sync service provider
final syncServiceProvider = Provider<SyncService>((ref) {
  return SyncService(ref);
});

/// sync state provider
final syncStateProvider =
    StateNotifierProvider<SyncStateNotifier, SyncState>((ref) {
  return SyncStateNotifier();
});

/// sync state
class SyncState {
  final bool isSyncing;
  final SyncStatus status;
  final String? currentSessionId;
  final int pendingChanges;
  final int unresolvedConflicts;
  final DateTime? lastSyncTime;
  final String? errorMessage;
  final double progress;

  const SyncState({
    this.isSyncing = false,
    this.status = SyncStatus.pending,
    this.currentSessionId,
    this.pendingChanges = 0,
    this.unresolvedConflicts = 0,
    this.lastSyncTime,
    this.errorMessage,
    this.progress = 0.0,
  });

  SyncState copyWith({
    bool? isSyncing,
    SyncStatus? status,
    String? currentSessionId,
    int? pendingChanges,
    int? unresolvedConflicts,
    DateTime? lastSyncTime,
    String? errorMessage,
    double? progress,
  }) {
    return SyncState(
      isSyncing: isSyncing ?? this.isSyncing,
      status: status ?? this.status,
      currentSessionId: currentSessionId ?? this.currentSessionId,
      pendingChanges: pendingChanges ?? this.pendingChanges,
      unresolvedConflicts: unresolvedConflicts ?? this.unresolvedConflicts,
      lastSyncTime: lastSyncTime ?? this.lastSyncTime,
      errorMessage: errorMessage,
      progress: progress ?? this.progress,
    );
  }
}

/// sync state notifier
class SyncStateNotifier extends StateNotifier<SyncState> {
  SyncStateNotifier() : super(const SyncState());

  void startSync(String sessionId) {
    state = state.copyWith(
      isSyncing: true,
      status: SyncStatus.inProgress,
      currentSessionId: sessionId,
      errorMessage: null,
      progress: 0.0,
    );
  }

  void updateProgress(double progress) {
    state = state.copyWith(progress: progress);
  }

  void completeSync() {
    state = state.copyWith(
      isSyncing: false,
      status: SyncStatus.completed,
      lastSyncTime: DateTime.now(),
      progress: 1.0,
    );
  }

  void failSync(String error) {
    state = state.copyWith(
      isSyncing: false,
      status: SyncStatus.failed,
      errorMessage: error,
    );
  }

  void setConflict(int count) {
    state = state.copyWith(
      status: SyncStatus.conflict,
      unresolvedConflicts: count,
    );
  }

  void updatePendingChanges(int count) {
    state = state.copyWith(pendingChanges: count);
  }

  void reset() {
    state = const SyncState();
  }
}

/// main sync service
class SyncService {
  final Ref _ref;
  static const String _nodeIdKey = 'unibos_node_id';
  static const String _nodeHostnameKey = 'unibos_node_hostname';
  static const String _versionVectorKey = 'unibos_version_vector';

  SyncService(this._ref);

  ApiClient get _apiClient => _ref.read(apiClientProvider);
  SyncStateNotifier get _syncState => _ref.read(syncStateProvider.notifier);
  OfflineQueue get _offlineQueue => _ref.read(offlineQueueProvider);

  /// get node id from storage
  Future<String?> getNodeId() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString(_nodeIdKey);
  }

  /// set node id
  Future<void> setNodeId(String nodeId) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_nodeIdKey, nodeId);
  }

  /// get node hostname
  Future<String> getNodeHostname() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString(_nodeHostnameKey) ?? 'mobile-device';
  }

  /// set node hostname
  Future<void> setNodeHostname(String hostname) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_nodeHostnameKey, hostname);
  }

  /// get local version vector
  Future<Map<String, int>> getVersionVector() async {
    final prefs = await SharedPreferences.getInstance();
    final json = prefs.getString(_versionVectorKey);
    if (json == null) return {};
    // Simple JSON parsing for version vector
    final map = <String, int>{};
    final clean = json.replaceAll('{', '').replaceAll('}', '');
    if (clean.isEmpty) return map;
    for (final pair in clean.split(',')) {
      final kv = pair.split(':');
      if (kv.length == 2) {
        map[kv[0].trim().replaceAll('"', '')] = int.tryParse(kv[1].trim()) ?? 0;
      }
    }
    return map;
  }

  /// save version vector
  Future<void> saveVersionVector(Map<String, int> vector) async {
    final prefs = await SharedPreferences.getInstance();
    final json = vector.entries.map((e) => '"${e.key}":${e.value}').join(',');
    await prefs.setString(_versionVectorKey, '{$json}');
  }

  /// get sync status from server
  Future<SyncStatusResponse?> getSyncStatus() async {
    try {
      final nodeId = await getNodeId();
      if (nodeId == null) return null;

      final response = await _apiClient.get<Map<String, dynamic>>(
        Endpoints.syncStatus,
        queryParameters: {'node_id': nodeId},
      );

      return SyncStatusResponse.fromJson(response);
    } on ApiException catch (e) {
      _syncState.failSync(e.message);
      return null;
    }
  }

  /// initialize sync session
  Future<SyncInitResponse?> initSync({
    List<String>? modules,
    String direction = 'bidirectional',
  }) async {
    try {
      final nodeId = await getNodeId();
      final hostname = await getNodeHostname();
      final versionVector = await getVersionVector();

      if (nodeId == null) {
        _syncState.failSync('Node ID not configured');
        return null;
      }

      final response = await _apiClient.post<Map<String, dynamic>>(
        Endpoints.syncInit,
        data: {
          'node_id': nodeId,
          'node_hostname': hostname,
          'direction': direction,
          'modules': modules ?? [],
          'version_vector': versionVector,
        },
      );

      final initResponse = SyncInitResponse.fromJson(response);
      _syncState.startSync(initResponse.sessionId);

      return initResponse;
    } on ApiException catch (e) {
      _syncState.failSync(e.message);
      return null;
    }
  }

  /// push local changes to hub
  Future<SyncPushResponse?> pushChanges(
    String sessionId,
    List<SyncRecord> records,
  ) async {
    try {
      final response = await _apiClient.post<Map<String, dynamic>>(
        Endpoints.syncPush,
        data: {
          'session_id': sessionId,
          'records': records.map((r) => r.toJson()).toList(),
        },
      );

      final pushResponse = SyncPushResponse.fromJson(response);

      if (pushResponse.conflicts > 0) {
        _syncState.setConflict(pushResponse.conflicts);
      }

      return pushResponse;
    } on ApiException catch (e) {
      _syncState.failSync(e.message);
      return null;
    }
  }

  /// pull changes from hub
  Future<List<SyncRecord>> pullChanges(
    String sessionId, {
    int batchSize = 100,
    int offset = 0,
    List<String>? models,
  }) async {
    try {
      final response = await _apiClient.post<Map<String, dynamic>>(
        Endpoints.syncPull,
        data: {
          'session_id': sessionId,
          'batch_size': batchSize,
          'offset': offset,
          'models': models ?? [],
        },
      );

      final records = (response['records'] as List<dynamic>?)
              ?.map((r) => SyncRecord.fromJson(r as Map<String, dynamic>))
              .toList() ??
          [];

      return records;
    } on ApiException catch (e) {
      _syncState.failSync(e.message);
      return [];
    }
  }

  /// complete sync session
  Future<bool> completeSync(String sessionId) async {
    try {
      final response = await _apiClient.post<Map<String, dynamic>>(
        Endpoints.syncComplete,
        data: {'session_id': sessionId},
      );

      final status = response['status']?.toString();
      if (status == 'completed') {
        _syncState.completeSync();
        return true;
      } else if (status == 'conflict') {
        final unresolvedConflicts = response['unresolved_conflicts'] as int? ?? 0;
        _syncState.setConflict(unresolvedConflicts);
        return false;
      }

      return false;
    } on ApiException catch (e) {
      _syncState.failSync(e.message);
      return false;
    }
  }

  /// get unresolved conflicts
  Future<List<SyncConflict>> getConflicts({bool unresolvedOnly = true}) async {
    try {
      final nodeId = await getNodeId();
      if (nodeId == null) return [];

      final response = await _apiClient.get<Map<String, dynamic>>(
        Endpoints.syncConflicts,
        queryParameters: {
          'node_id': nodeId,
          'resolved': (!unresolvedOnly).toString(),
        },
      );

      final results = response['results'] as List<dynamic>? ?? [];
      return results
          .map((r) => SyncConflict.fromJson(r as Map<String, dynamic>))
          .toList();
    } on ApiException {
      return [];
    }
  }

  /// resolve a conflict
  Future<bool> resolveConflict(
    String conflictId,
    ConflictStrategy strategy, {
    Map<String, dynamic>? resolutionData,
  }) async {
    try {
      await _apiClient.post<Map<String, dynamic>>(
        '${Endpoints.syncConflicts}$conflictId/resolve/',
        data: {
          'strategy': strategy.name,
          if (resolutionData != null) 'resolution_data': resolutionData,
        },
      );

      return true;
    } on ApiException {
      return false;
    }
  }

  /// perform full sync operation
  Future<SyncResult> performSync({
    List<String>? modules,
    bool pushFirst = true,
  }) async {
    // Check for offline operations first
    final pendingOperations = await _offlineQueue.getPendingOperations();

    // Initialize sync
    final initResponse = await initSync(modules: modules);
    if (initResponse == null) {
      return SyncResult(
        success: false,
        error: 'Failed to initialize sync',
      );
    }

    final sessionId = initResponse.sessionId;
    var pushed = 0;
    var pulled = 0;
    var conflicts = 0;

    // Push offline operations first
    if (pushFirst && pendingOperations.isNotEmpty) {
      final records = pendingOperations
          .map((op) => SyncRecord(
                modelName: op.modelName,
                recordId: op.recordId,
                operation: op.operation,
                data: op.data,
                localVersion: op.localVersion,
                localModifiedAt: op.createdAt,
              ))
          .toList();

      final pushResponse = await pushChanges(sessionId, records);
      if (pushResponse != null) {
        pushed = pushResponse.accepted;
        conflicts += pushResponse.conflicts;

        // Clear successfully pushed operations
        for (final op in pendingOperations) {
          await _offlineQueue.markCompleted(op.id);
        }
      }
    }

    _syncState.updateProgress(0.5);

    // Pull changes from hub
    final pulledRecords = await pullChanges(sessionId);
    pulled = pulledRecords.length;

    // TODO: Apply pulled changes to local storage

    _syncState.updateProgress(0.9);

    // Complete sync
    final completed = await completeSync(sessionId);

    if (completed) {
      // Update version vector
      final newVector = await getVersionVector();
      for (final entry in initResponse.hubVersionVector.entries) {
        newVector[entry.key] = entry.value;
      }
      await saveVersionVector(newVector);
    }

    return SyncResult(
      success: completed,
      pushed: pushed,
      pulled: pulled,
      conflicts: conflicts,
    );
  }

  /// queue operation for offline sync
  Future<void> queueOfflineOperation(
    String modelName,
    String recordId,
    SyncOperation operation,
    Map<String, dynamic> data,
  ) async {
    final versionVector = await getVersionVector();
    final localVersion = (versionVector[modelName] ?? 0) + 1;

    await _offlineQueue.addOperation(
      modelName: modelName,
      recordId: recordId,
      operation: operation,
      data: data,
      localVersion: localVersion,
    );

    // Update version vector
    versionVector[modelName] = localVersion;
    await saveVersionVector(versionVector);

    // Update pending count in state
    final count = await _offlineQueue.getPendingCount();
    _syncState.updatePendingChanges(count);
  }
}

/// sync result
class SyncResult {
  final bool success;
  final int pushed;
  final int pulled;
  final int conflicts;
  final String? error;

  SyncResult({
    required this.success,
    this.pushed = 0,
    this.pulled = 0,
    this.conflicts = 0,
    this.error,
  });
}
