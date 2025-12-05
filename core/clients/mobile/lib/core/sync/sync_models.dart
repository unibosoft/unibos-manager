/// sync data models for flutter client
library;

/// sync session status enum
enum SyncStatus {
  pending,
  inProgress,
  completed,
  failed,
  conflict,
}

/// sync operation type
enum SyncOperation {
  create,
  update,
  delete,
}

/// conflict resolution strategy
enum ConflictStrategy {
  newerWins,
  hubWins,
  nodeWins,
  manual,
  keepBoth,
}

/// sync session model
class SyncSession {
  final String sessionId;
  final String nodeId;
  final String nodeHostname;
  final String direction;
  final List<String> modules;
  final Map<String, int> nodeVersionVector;
  final Map<String, int> hubVersionVector;
  final int totalRecords;
  final int processedRecords;
  final int conflictsCount;
  final SyncStatus status;
  final DateTime? startedAt;
  final DateTime? completedAt;

  SyncSession({
    required this.sessionId,
    required this.nodeId,
    required this.nodeHostname,
    this.direction = 'bidirectional',
    this.modules = const [],
    this.nodeVersionVector = const {},
    this.hubVersionVector = const {},
    this.totalRecords = 0,
    this.processedRecords = 0,
    this.conflictsCount = 0,
    this.status = SyncStatus.pending,
    this.startedAt,
    this.completedAt,
  });

  factory SyncSession.fromJson(Map<String, dynamic> json) {
    return SyncSession(
      sessionId: json['session_id']?.toString() ?? '',
      nodeId: json['node_id']?.toString() ?? '',
      nodeHostname: json['node_hostname']?.toString() ?? '',
      direction: json['direction']?.toString() ?? 'bidirectional',
      modules: (json['modules'] as List<dynamic>?)
              ?.map((e) => e.toString())
              .toList() ??
          [],
      nodeVersionVector:
          (json['node_version_vector'] as Map<String, dynamic>?)
                  ?.map((k, v) => MapEntry(k, v as int)) ??
              {},
      hubVersionVector: (json['hub_version_vector'] as Map<String, dynamic>?)
              ?.map((k, v) => MapEntry(k, v as int)) ??
          {},
      totalRecords: json['total_records'] as int? ?? 0,
      processedRecords: json['processed_records'] as int? ?? 0,
      conflictsCount: json['conflicts_count'] as int? ?? 0,
      status: _parseStatus(json['status']),
      startedAt: json['started_at'] != null
          ? DateTime.parse(json['started_at'])
          : null,
      completedAt: json['completed_at'] != null
          ? DateTime.parse(json['completed_at'])
          : null,
    );
  }

  static SyncStatus _parseStatus(dynamic status) {
    switch (status?.toString()) {
      case 'pending':
        return SyncStatus.pending;
      case 'in_progress':
        return SyncStatus.inProgress;
      case 'completed':
        return SyncStatus.completed;
      case 'failed':
        return SyncStatus.failed;
      case 'conflict':
        return SyncStatus.conflict;
      default:
        return SyncStatus.pending;
    }
  }
}

/// sync record model
class SyncRecord {
  final String? id;
  final String modelName;
  final String recordId;
  final SyncOperation operation;
  final Map<String, dynamic> data;
  final int localVersion;
  final int? remoteVersion;
  final DateTime? localModifiedAt;
  final DateTime? remoteModifiedAt;
  final SyncStatus status;
  final DateTime? syncedAt;

  SyncRecord({
    this.id,
    required this.modelName,
    required this.recordId,
    required this.operation,
    this.data = const {},
    this.localVersion = 0,
    this.remoteVersion,
    this.localModifiedAt,
    this.remoteModifiedAt,
    this.status = SyncStatus.pending,
    this.syncedAt,
  });

  factory SyncRecord.fromJson(Map<String, dynamic> json) {
    return SyncRecord(
      id: json['id']?.toString(),
      modelName: json['model_name']?.toString() ?? '',
      recordId: json['record_id']?.toString() ?? '',
      operation: _parseOperation(json['operation']),
      data: (json['data'] as Map<String, dynamic>?) ?? {},
      localVersion: json['local_version'] as int? ?? 0,
      remoteVersion: json['remote_version'] as int?,
      localModifiedAt: json['local_modified_at'] != null
          ? DateTime.parse(json['local_modified_at'])
          : null,
      remoteModifiedAt: json['remote_modified_at'] != null
          ? DateTime.parse(json['remote_modified_at'])
          : null,
      status: SyncSession._parseStatus(json['status']),
      syncedAt:
          json['synced_at'] != null ? DateTime.parse(json['synced_at']) : null,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'model_name': modelName,
      'record_id': recordId,
      'operation': operation.name,
      'data': data,
      'local_version': localVersion,
      'local_modified_at': localModifiedAt?.toIso8601String(),
    };
  }

  static SyncOperation _parseOperation(dynamic op) {
    switch (op?.toString()) {
      case 'create':
        return SyncOperation.create;
      case 'update':
        return SyncOperation.update;
      case 'delete':
        return SyncOperation.delete;
      default:
        return SyncOperation.update;
    }
  }
}

/// sync conflict model
class SyncConflict {
  final String id;
  final String sessionId;
  final String modelName;
  final String recordId;
  final Map<String, dynamic> localData;
  final Map<String, dynamic> remoteData;
  final DateTime localModifiedAt;
  final DateTime remoteModifiedAt;
  final String localNodeId;
  final String remoteSource;
  final ConflictStrategy strategy;
  final bool resolved;
  final Map<String, dynamic>? resolutionData;
  final DateTime? resolvedAt;

  SyncConflict({
    required this.id,
    required this.sessionId,
    required this.modelName,
    required this.recordId,
    required this.localData,
    required this.remoteData,
    required this.localModifiedAt,
    required this.remoteModifiedAt,
    required this.localNodeId,
    required this.remoteSource,
    this.strategy = ConflictStrategy.manual,
    this.resolved = false,
    this.resolutionData,
    this.resolvedAt,
  });

  factory SyncConflict.fromJson(Map<String, dynamic> json) {
    return SyncConflict(
      id: json['id']?.toString() ?? '',
      sessionId: json['session_id']?.toString() ?? '',
      modelName: json['model_name']?.toString() ?? '',
      recordId: json['record_id']?.toString() ?? '',
      localData: (json['local_data'] as Map<String, dynamic>?) ?? {},
      remoteData: (json['remote_data'] as Map<String, dynamic>?) ?? {},
      localModifiedAt: DateTime.parse(
          json['local_modified_at'] ?? DateTime.now().toIso8601String()),
      remoteModifiedAt: DateTime.parse(
          json['remote_modified_at'] ?? DateTime.now().toIso8601String()),
      localNodeId: json['local_node_id']?.toString() ?? '',
      remoteSource: json['remote_source']?.toString() ?? 'hub',
      strategy: _parseStrategy(json['strategy']),
      resolved: json['resolved'] as bool? ?? false,
      resolutionData: json['resolution_data'] as Map<String, dynamic>?,
      resolvedAt: json['resolved_at'] != null
          ? DateTime.parse(json['resolved_at'])
          : null,
    );
  }

  static ConflictStrategy _parseStrategy(dynamic strategy) {
    switch (strategy?.toString()) {
      case 'newer_wins':
        return ConflictStrategy.newerWins;
      case 'hub_wins':
        return ConflictStrategy.hubWins;
      case 'node_wins':
        return ConflictStrategy.nodeWins;
      case 'keep_both':
        return ConflictStrategy.keepBoth;
      case 'manual':
      default:
        return ConflictStrategy.manual;
    }
  }
}

/// sync status response
class SyncStatusResponse {
  final String nodeId;
  final bool isSynced;
  final DateTime? lastSync;
  final int pendingPush;
  final int pendingPull;
  final int unresolvedConflicts;
  final int offlineOperations;
  final Map<String, int> versionVectors;

  SyncStatusResponse({
    required this.nodeId,
    required this.isSynced,
    this.lastSync,
    this.pendingPush = 0,
    this.pendingPull = 0,
    this.unresolvedConflicts = 0,
    this.offlineOperations = 0,
    this.versionVectors = const {},
  });

  factory SyncStatusResponse.fromJson(Map<String, dynamic> json) {
    return SyncStatusResponse(
      nodeId: json['node_id']?.toString() ?? '',
      isSynced: json['is_synced'] as bool? ?? false,
      lastSync:
          json['last_sync'] != null ? DateTime.parse(json['last_sync']) : null,
      pendingPush: json['pending_push'] as int? ?? 0,
      pendingPull: json['pending_pull'] as int? ?? 0,
      unresolvedConflicts: json['unresolved_conflicts'] as int? ?? 0,
      offlineOperations: json['offline_operations'] as int? ?? 0,
      versionVectors: (json['version_vectors'] as Map<String, dynamic>?)
              ?.map((k, v) => MapEntry(k, v as int)) ??
          {},
    );
  }
}

/// sync init response
class SyncInitResponse {
  final String sessionId;
  final Map<String, int> hubVersionVector;
  final int changesAvailable;
  final int conflictsDetected;
  final List<String> modules;

  SyncInitResponse({
    required this.sessionId,
    this.hubVersionVector = const {},
    this.changesAvailable = 0,
    this.conflictsDetected = 0,
    this.modules = const [],
  });

  factory SyncInitResponse.fromJson(Map<String, dynamic> json) {
    return SyncInitResponse(
      sessionId: json['session_id']?.toString() ?? '',
      hubVersionVector: (json['hub_version_vector'] as Map<String, dynamic>?)
              ?.map((k, v) => MapEntry(k, v as int)) ??
          {},
      changesAvailable: json['changes_available'] as int? ?? 0,
      conflictsDetected: json['conflicts_detected'] as int? ?? 0,
      modules: (json['modules'] as List<dynamic>?)
              ?.map((e) => e.toString())
              .toList() ??
          [],
    );
  }
}

/// sync push response
class SyncPushResponse {
  final int accepted;
  final int rejected;
  final int conflicts;
  final List<Map<String, dynamic>> errors;

  SyncPushResponse({
    this.accepted = 0,
    this.rejected = 0,
    this.conflicts = 0,
    this.errors = const [],
  });

  factory SyncPushResponse.fromJson(Map<String, dynamic> json) {
    return SyncPushResponse(
      accepted: json['accepted'] as int? ?? 0,
      rejected: json['rejected'] as int? ?? 0,
      conflicts: json['conflicts'] as int? ?? 0,
      errors: (json['errors'] as List<dynamic>?)
              ?.map((e) => e as Map<String, dynamic>)
              .toList() ??
          [],
    );
  }
}
