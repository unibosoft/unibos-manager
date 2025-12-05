import 'dart:convert';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'sync_models.dart';

/// offline queue provider
final offlineQueueProvider = Provider<OfflineQueue>((ref) {
  return OfflineQueue();
});

/// offline operation model
class OfflineOperation {
  final String id;
  final String modelName;
  final String recordId;
  final SyncOperation operation;
  final Map<String, dynamic> data;
  final int localVersion;
  final DateTime createdAt;
  final int retryCount;
  final String status;

  OfflineOperation({
    required this.id,
    required this.modelName,
    required this.recordId,
    required this.operation,
    this.data = const {},
    this.localVersion = 0,
    DateTime? createdAt,
    this.retryCount = 0,
    this.status = 'pending',
  }) : createdAt = createdAt ?? DateTime.now();

  factory OfflineOperation.fromJson(Map<String, dynamic> json) {
    return OfflineOperation(
      id: json['id']?.toString() ?? '',
      modelName: json['model_name']?.toString() ?? '',
      recordId: json['record_id']?.toString() ?? '',
      operation: _parseOperation(json['operation']),
      data: (json['data'] as Map<String, dynamic>?) ?? {},
      localVersion: json['local_version'] as int? ?? 0,
      createdAt: json['created_at'] != null
          ? DateTime.parse(json['created_at'])
          : DateTime.now(),
      retryCount: json['retry_count'] as int? ?? 0,
      status: json['status']?.toString() ?? 'pending',
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'model_name': modelName,
      'record_id': recordId,
      'operation': operation.name,
      'data': data,
      'local_version': localVersion,
      'created_at': createdAt.toIso8601String(),
      'retry_count': retryCount,
      'status': status,
    };
  }

  OfflineOperation copyWith({
    String? id,
    String? modelName,
    String? recordId,
    SyncOperation? operation,
    Map<String, dynamic>? data,
    int? localVersion,
    DateTime? createdAt,
    int? retryCount,
    String? status,
  }) {
    return OfflineOperation(
      id: id ?? this.id,
      modelName: modelName ?? this.modelName,
      recordId: recordId ?? this.recordId,
      operation: operation ?? this.operation,
      data: data ?? this.data,
      localVersion: localVersion ?? this.localVersion,
      createdAt: createdAt ?? this.createdAt,
      retryCount: retryCount ?? this.retryCount,
      status: status ?? this.status,
    );
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

/// offline queue for managing pending sync operations
class OfflineQueue {
  static const String _queueKey = 'unibos_offline_queue';
  static const int maxRetries = 3;

  /// get all operations
  Future<List<OfflineOperation>> getAllOperations() async {
    final prefs = await SharedPreferences.getInstance();
    final json = prefs.getString(_queueKey);
    if (json == null) return [];

    try {
      final list = jsonDecode(json) as List<dynamic>;
      return list
          .map((e) => OfflineOperation.fromJson(e as Map<String, dynamic>))
          .toList();
    } catch (e) {
      return [];
    }
  }

  /// get pending operations only
  Future<List<OfflineOperation>> getPendingOperations() async {
    final all = await getAllOperations();
    return all.where((op) => op.status == 'pending').toList();
  }

  /// get pending count
  Future<int> getPendingCount() async {
    final pending = await getPendingOperations();
    return pending.length;
  }

  /// save all operations
  Future<void> _saveAll(List<OfflineOperation> operations) async {
    final prefs = await SharedPreferences.getInstance();
    final json = jsonEncode(operations.map((e) => e.toJson()).toList());
    await prefs.setString(_queueKey, json);
  }

  /// add new operation
  Future<String> addOperation({
    required String modelName,
    required String recordId,
    required SyncOperation operation,
    Map<String, dynamic> data = const {},
    int localVersion = 0,
  }) async {
    final operations = await getAllOperations();

    // Check if there's already an operation for this record
    final existingIndex = operations.indexWhere(
      (op) =>
          op.modelName == modelName &&
          op.recordId == recordId &&
          op.status == 'pending',
    );

    final id = DateTime.now().millisecondsSinceEpoch.toString();
    final newOp = OfflineOperation(
      id: id,
      modelName: modelName,
      recordId: recordId,
      operation: operation,
      data: data,
      localVersion: localVersion,
    );

    if (existingIndex != -1) {
      // Merge operations
      final existing = operations[existingIndex];
      if (operation == SyncOperation.delete) {
        // Delete overrides previous operations
        if (existing.operation == SyncOperation.create) {
          // Remove both - never synced, now deleted
          operations.removeAt(existingIndex);
        } else {
          operations[existingIndex] = newOp;
        }
      } else {
        // Update with latest data
        operations[existingIndex] = newOp.copyWith(
          id: existing.id,
          localVersion: existing.localVersion + 1,
        );
      }
    } else {
      operations.add(newOp);
    }

    await _saveAll(operations);
    return id;
  }

  /// mark operation as completed
  Future<void> markCompleted(String id) async {
    final operations = await getAllOperations();
    final index = operations.indexWhere((op) => op.id == id);
    if (index != -1) {
      operations[index] = operations[index].copyWith(status: 'completed');
      await _saveAll(operations);
    }
  }

  /// mark operation as failed and increment retry
  Future<void> markFailed(String id) async {
    final operations = await getAllOperations();
    final index = operations.indexWhere((op) => op.id == id);
    if (index != -1) {
      final op = operations[index];
      if (op.retryCount >= maxRetries) {
        operations[index] = op.copyWith(status: 'failed');
      } else {
        operations[index] = op.copyWith(retryCount: op.retryCount + 1);
      }
      await _saveAll(operations);
    }
  }

  /// remove operation
  Future<void> removeOperation(String id) async {
    final operations = await getAllOperations();
    operations.removeWhere((op) => op.id == id);
    await _saveAll(operations);
  }

  /// clear completed operations
  Future<int> clearCompleted() async {
    final operations = await getAllOperations();
    final originalCount = operations.length;
    operations.removeWhere((op) => op.status == 'completed');
    await _saveAll(operations);
    return originalCount - operations.length;
  }

  /// clear all operations
  Future<void> clearAll() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(_queueKey);
  }

  /// get operation by id
  Future<OfflineOperation?> getOperation(String id) async {
    final operations = await getAllOperations();
    try {
      return operations.firstWhere((op) => op.id == id);
    } catch (_) {
      return null;
    }
  }

  /// get operations for a specific model
  Future<List<OfflineOperation>> getOperationsForModel(String modelName) async {
    final all = await getAllOperations();
    return all.where((op) => op.modelName == modelName).toList();
  }
}
