/// Attachment Service
///
/// Encrypted file attachment management for messenger.
/// Handles file encryption, upload, download, and decryption.

import 'dart:convert';
import 'dart:typed_data';
import 'package:cryptography/cryptography.dart';

/// Encrypted file attachment data
class EncryptedAttachment {
  final Uint8List encryptedData;
  final String fileNonce;
  final String encryptedFileKey;
  final String fileHash;
  final String? encryptedMetadata;

  EncryptedAttachment({
    required this.encryptedData,
    required this.fileNonce,
    required this.encryptedFileKey,
    required this.fileHash,
    this.encryptedMetadata,
  });
}

/// Decrypted file attachment data
class DecryptedAttachment {
  final Uint8List data;
  final String originalFilename;
  final String mimeType;
  final int fileSize;
  final Map<String, dynamic>? metadata;

  DecryptedAttachment({
    required this.data,
    required this.originalFilename,
    required this.mimeType,
    required this.fileSize,
    this.metadata,
  });
}

/// Attachment metadata
class AttachmentMetadata {
  final String id;
  final String originalFilename;
  final String fileType;
  final int fileSize;
  final String encryptedFileKey;
  final String fileNonce;
  final String fileHash;
  final String? encryptedThumbnailKey;
  final String? encryptedMetadata;
  final bool isProcessed;
  final DateTime createdAt;

  AttachmentMetadata({
    required this.id,
    required this.originalFilename,
    required this.fileType,
    required this.fileSize,
    required this.encryptedFileKey,
    required this.fileNonce,
    required this.fileHash,
    this.encryptedThumbnailKey,
    this.encryptedMetadata,
    required this.isProcessed,
    required this.createdAt,
  });

  factory AttachmentMetadata.fromJson(Map<String, dynamic> json) {
    return AttachmentMetadata(
      id: json['id'],
      originalFilename: json['original_filename'],
      fileType: json['file_type'],
      fileSize: json['file_size'],
      encryptedFileKey: json['encrypted_file_key'],
      fileNonce: json['file_nonce'],
      fileHash: json['file_hash'],
      encryptedThumbnailKey: json['encrypted_thumbnail_key'],
      encryptedMetadata: json['encrypted_metadata'],
      isProcessed: json['is_processed'] ?? false,
      createdAt: DateTime.parse(json['created_at']),
    );
  }
}

/// Service for handling encrypted file attachments
class AttachmentService {
  final _aesGcm = AesGcm.with256bits();
  final _sha256 = Sha256();

  /// Encrypt a file for upload
  ///
  /// Returns encrypted data along with encrypted file key.
  /// The file key is encrypted with the message key for E2E security.
  Future<EncryptedAttachment> encryptFile({
    required Uint8List fileData,
    required SecretKey messageKey,
    Map<String, dynamic>? metadata,
  }) async {
    // Generate unique file encryption key
    final fileKey = await _aesGcm.newSecretKey();
    final fileKeyBytes = await fileKey.extractBytes();

    // Generate nonce for file encryption
    final fileNonce = _aesGcm.newNonce();

    // Encrypt file data
    final secretBox = await _aesGcm.encrypt(
      fileData,
      secretKey: fileKey,
      nonce: fileNonce,
    );

    // Calculate hash of encrypted data
    final encryptedData = Uint8List.fromList([
      ...secretBox.nonce,
      ...secretBox.cipherText,
      ...secretBox.mac.bytes,
    ]);
    final hashDigest = await _sha256.hash(encryptedData);
    final fileHash = hashDigest.bytes.map((b) => b.toRadixString(16).padLeft(2, '0')).join();

    // Encrypt file key with message key
    final keyNonce = _aesGcm.newNonce();
    final encryptedKeyBox = await _aesGcm.encrypt(
      Uint8List.fromList(fileKeyBytes),
      secretKey: messageKey,
      nonce: keyNonce,
    );

    // Combine nonce + ciphertext + mac for encrypted key
    final encryptedFileKey = base64Encode([
      ...encryptedKeyBox.nonce,
      ...encryptedKeyBox.cipherText,
      ...encryptedKeyBox.mac.bytes,
    ]);

    // Encrypt metadata if provided
    String? encryptedMetadata;
    if (metadata != null) {
      final metadataJson = utf8.encode(jsonEncode(metadata));
      final metadataNonce = _aesGcm.newNonce();
      final metadataBox = await _aesGcm.encrypt(
        metadataJson,
        secretKey: fileKey,
        nonce: metadataNonce,
      );
      encryptedMetadata = base64Encode([
        ...metadataBox.nonce,
        ...metadataBox.cipherText,
        ...metadataBox.mac.bytes,
      ]);
    }

    return EncryptedAttachment(
      encryptedData: encryptedData,
      fileNonce: base64Encode(fileNonce),
      encryptedFileKey: encryptedFileKey,
      fileHash: fileHash,
      encryptedMetadata: encryptedMetadata,
    );
  }

  /// Decrypt a downloaded file
  ///
  /// Decrypts the file key using the message key, then decrypts the file.
  Future<Uint8List> decryptFile({
    required Uint8List encryptedData,
    required String encryptedFileKey,
    required SecretKey messageKey,
  }) async {
    // Decode encrypted file key
    final encryptedKeyBytes = base64Decode(encryptedFileKey);

    // Extract components (nonce: 12 bytes, mac: 16 bytes)
    final keyNonce = encryptedKeyBytes.sublist(0, 12);
    final keyCiphertext = encryptedKeyBytes.sublist(12, encryptedKeyBytes.length - 16);
    final keyMac = encryptedKeyBytes.sublist(encryptedKeyBytes.length - 16);

    // Decrypt file key
    final keyBox = SecretBox(
      keyCiphertext,
      nonce: keyNonce,
      mac: Mac(keyMac),
    );
    final fileKeyBytes = await _aesGcm.decrypt(keyBox, secretKey: messageKey);
    final fileKey = SecretKey(fileKeyBytes);

    // Extract file encryption components
    final fileNonce = encryptedData.sublist(0, 12);
    final fileCiphertext = encryptedData.sublist(12, encryptedData.length - 16);
    final fileMac = encryptedData.sublist(encryptedData.length - 16);

    // Decrypt file
    final fileBox = SecretBox(
      fileCiphertext,
      nonce: fileNonce,
      mac: Mac(fileMac),
    );
    final decryptedBytes = await _aesGcm.decrypt(fileBox, secretKey: fileKey);

    return Uint8List.fromList(decryptedBytes);
  }

  /// Decrypt file metadata
  Future<Map<String, dynamic>?> decryptMetadata({
    required String encryptedMetadata,
    required String encryptedFileKey,
    required SecretKey messageKey,
  }) async {
    if (encryptedMetadata.isEmpty) return null;

    // First decrypt the file key
    final encryptedKeyBytes = base64Decode(encryptedFileKey);
    final keyNonce = encryptedKeyBytes.sublist(0, 12);
    final keyCiphertext = encryptedKeyBytes.sublist(12, encryptedKeyBytes.length - 16);
    final keyMac = encryptedKeyBytes.sublist(encryptedKeyBytes.length - 16);

    final keyBox = SecretBox(
      keyCiphertext,
      nonce: keyNonce,
      mac: Mac(keyMac),
    );
    final fileKeyBytes = await _aesGcm.decrypt(keyBox, secretKey: messageKey);
    final fileKey = SecretKey(fileKeyBytes);

    // Decrypt metadata with file key
    final metadataBytes = base64Decode(encryptedMetadata);
    final metaNonce = metadataBytes.sublist(0, 12);
    final metaCiphertext = metadataBytes.sublist(12, metadataBytes.length - 16);
    final metaMac = metadataBytes.sublist(metadataBytes.length - 16);

    final metaBox = SecretBox(
      metaCiphertext,
      nonce: metaNonce,
      mac: Mac(metaMac),
    );
    final decryptedMeta = await _aesGcm.decrypt(metaBox, secretKey: fileKey);

    return jsonDecode(utf8.decode(decryptedMeta)) as Map<String, dynamic>;
  }

  /// Verify file integrity
  Future<bool> verifyFileHash({
    required Uint8List encryptedData,
    required String expectedHash,
  }) async {
    final hashDigest = await _sha256.hash(encryptedData);
    final calculatedHash = hashDigest.bytes.map((b) => b.toRadixString(16).padLeft(2, '0')).join();
    return calculatedHash == expectedHash;
  }

  /// Generate thumbnail encryption key
  Future<String> encryptThumbnail({
    required Uint8List thumbnailData,
    required SecretKey messageKey,
  }) async {
    // Generate thumbnail key
    final thumbKey = await _aesGcm.newSecretKey();
    final thumbKeyBytes = await thumbKey.extractBytes();

    // Encrypt thumbnail
    final thumbNonce = _aesGcm.newNonce();
    final thumbBox = await _aesGcm.encrypt(
      thumbnailData,
      secretKey: thumbKey,
      nonce: thumbNonce,
    );

    // Encrypt thumbnail key with message key
    final keyNonce = _aesGcm.newNonce();
    final encryptedKeyBox = await _aesGcm.encrypt(
      Uint8List.fromList(thumbKeyBytes),
      secretKey: messageKey,
      nonce: keyNonce,
    );

    // Return base64 encoded encrypted thumbnail key
    return base64Encode([
      ...encryptedKeyBox.nonce,
      ...encryptedKeyBox.cipherText,
      ...encryptedKeyBox.mac.bytes,
    ]);
  }

  /// Get MIME type from file extension
  String getMimeType(String filename) {
    final ext = filename.split('.').last.toLowerCase();
    const mimeTypes = {
      'jpg': 'image/jpeg',
      'jpeg': 'image/jpeg',
      'png': 'image/png',
      'gif': 'image/gif',
      'webp': 'image/webp',
      'mp4': 'video/mp4',
      'webm': 'video/webm',
      'mp3': 'audio/mpeg',
      'wav': 'audio/wav',
      'ogg': 'audio/ogg',
      'pdf': 'application/pdf',
      'zip': 'application/zip',
      'txt': 'text/plain',
      'json': 'application/json',
    };
    return mimeTypes[ext] ?? 'application/octet-stream';
  }

  /// Check if file type is allowed
  bool isAllowedFileType(String mimeType) {
    const allowedTypes = [
      'image/jpeg',
      'image/png',
      'image/gif',
      'image/webp',
      'video/mp4',
      'video/webm',
      'audio/mpeg',
      'audio/wav',
      'audio/ogg',
      'application/pdf',
      'application/zip',
      'text/plain',
      'application/json',
    ];
    return allowedTypes.contains(mimeType);
  }

  /// Sanitize filename for safety
  String sanitizeFilename(String filename) {
    // Remove path traversal attempts
    var safe = filename.replaceAll(RegExp(r'\.\.'), '');
    safe = safe.replaceAll(RegExp(r'[/\\]'), '_');
    safe = safe.replaceAll(RegExp(r'[\x00-\x1f]'), '');
    safe = safe.replaceAll(RegExp(r'[<>:"|?*]'), '_');

    // Limit length
    if (safe.length > 255) {
      final ext = safe.contains('.') ? '.${safe.split('.').last}' : '';
      safe = '${safe.substring(0, 255 - ext.length)}$ext';
    }

    return safe.isEmpty ? 'unnamed_file' : safe;
  }
}
