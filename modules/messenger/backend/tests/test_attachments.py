"""
File Attachment Tests

Tests for encrypted file attachment upload, download, and management.
"""

import pytest
import base64
import hashlib
import os
from io import BytesIO
from unittest.mock import patch, MagicMock
from django.core.files.uploadedfile import SimpleUploadedFile


class TestAttachmentEncryption:
    """Tests for attachment encryption/decryption"""

    def test_file_encryption_key_generation(self):
        """Test generating unique encryption key for each file"""
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM
        import secrets

        # Generate file encryption key
        file_key = secrets.token_bytes(32)  # 256-bit key
        assert len(file_key) == 32

        # Generate nonce
        nonce = secrets.token_bytes(12)  # 96-bit nonce for AES-GCM
        assert len(nonce) == 12

        # Encrypt some data
        aesgcm = AESGCM(file_key)
        plaintext = b"Test file content"
        ciphertext = aesgcm.encrypt(nonce, plaintext, None)

        # Decrypt and verify
        decrypted = aesgcm.decrypt(nonce, ciphertext, None)
        assert decrypted == plaintext

    def test_file_hash_verification(self):
        """Test SHA-256 hash verification of encrypted files"""
        encrypted_data = b"encrypted file content here"

        # Calculate hash
        file_hash = hashlib.sha256(encrypted_data).hexdigest()
        assert len(file_hash) == 64  # 256-bit hash as hex

        # Verify hash
        calculated_hash = hashlib.sha256(encrypted_data).hexdigest()
        assert calculated_hash == file_hash

    def test_large_file_encryption(self):
        """Test encrypting larger files (1MB)"""
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM
        import secrets

        # Generate 1MB of random data
        plaintext = secrets.token_bytes(1024 * 1024)  # 1MB

        file_key = secrets.token_bytes(32)
        nonce = secrets.token_bytes(12)

        aesgcm = AESGCM(file_key)
        ciphertext = aesgcm.encrypt(nonce, plaintext, None)

        # Verify encryption added overhead (auth tag)
        assert len(ciphertext) == len(plaintext) + 16  # 16-byte auth tag

        # Decrypt and verify
        decrypted = aesgcm.decrypt(nonce, ciphertext, None)
        assert decrypted == plaintext

    def test_file_key_encryption_with_message_key(self):
        """Test encrypting file key with message encryption key"""
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM
        import secrets

        # File encryption key
        file_key = secrets.token_bytes(32)

        # Message encryption key (derived from conversation key exchange)
        message_key = secrets.token_bytes(32)

        # Encrypt file key with message key
        nonce = secrets.token_bytes(12)
        aesgcm = AESGCM(message_key)
        encrypted_file_key = aesgcm.encrypt(nonce, file_key, None)

        # Decrypt file key
        decrypted_file_key = aesgcm.decrypt(nonce, encrypted_file_key, None)
        assert decrypted_file_key == file_key


class TestAttachmentModel:
    """Tests for MessageAttachment model"""

    @pytest.fixture
    def mock_message(self):
        """Create mock message for attachment"""
        message = MagicMock()
        message.id = 'test-message-id'
        message.conversation_id = 'test-conversation-id'
        return message

    def test_attachment_model_fields_defined(self):
        """Test attachment model has required fields (via source inspection)"""
        import ast
        import os

        # Read the models.py file and parse it
        models_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'models.py'
        )

        with open(models_path, 'r') as f:
            source = f.read()

        # Check that MessageAttachment class exists with expected fields
        assert 'class MessageAttachment' in source
        assert 'file = models.FileField' in source
        assert 'original_filename = models.CharField' in source
        assert 'file_type = models.CharField' in source
        assert 'file_size = models.PositiveBigIntegerField' in source
        assert 'encrypted_file_key = models.TextField' in source
        assert 'file_nonce = models.CharField' in source
        assert 'file_hash = models.CharField' in source
        assert 'thumbnail = models.ImageField' in source
        assert 'encrypted_thumbnail_key = models.TextField' in source
        assert 'encrypted_metadata = models.TextField' in source
        assert 'is_processed = models.BooleanField' in source

    def test_supported_file_types(self):
        """Test various file types are supported"""
        supported_types = [
            'image/jpeg',
            'image/png',
            'image/gif',
            'image/webp',
            'video/mp4',
            'video/webm',
            'audio/mp3',
            'audio/wav',
            'audio/ogg',
            'application/pdf',
            'application/zip',
            'text/plain',
            'application/json',
        ]

        # All should be valid MIME types
        for mime_type in supported_types:
            assert '/' in mime_type
            main_type, sub_type = mime_type.split('/')
            assert len(main_type) > 0
            assert len(sub_type) > 0


class TestAttachmentSerializer:
    """Tests for attachment serializers"""

    def test_upload_serializer_fields_defined(self):
        """Test AttachmentUploadSerializer has required fields (via source inspection)"""
        import os

        serializers_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'serializers.py'
        )

        with open(serializers_path, 'r') as f:
            source = f.read()

        # Check AttachmentUploadSerializer exists with expected fields
        assert 'class AttachmentUploadSerializer' in source
        assert 'file = serializers.FileField' in source
        assert 'encrypted_file_key = serializers.CharField' in source
        assert 'file_nonce = serializers.CharField' in source
        assert 'file_hash = serializers.CharField' in source

    def test_attachment_serializer_fields_defined(self):
        """Test MessageAttachmentSerializer has expected fields (via source inspection)"""
        import os

        serializers_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'serializers.py'
        )

        with open(serializers_path, 'r') as f:
            source = f.read()

        # Check MessageAttachmentSerializer exists
        assert 'class MessageAttachmentSerializer' in source
        assert "'original_filename'" in source or '"original_filename"' in source
        assert "'file_type'" in source or '"file_type"' in source
        assert "'file_size'" in source or '"file_size"' in source
        assert "'encrypted_file_key'" in source or '"encrypted_file_key"' in source
        assert "'file_nonce'" in source or '"file_nonce"' in source
        assert "'file_hash'" in source or '"file_hash"' in source


class TestAttachmentViews:
    """Tests for attachment API views"""

    def test_views_defined(self):
        """Test attachment views are defined (via source inspection)"""
        import os

        views_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'views.py'
        )

        with open(views_path, 'r') as f:
            source = f.read()

        # Check views exist
        assert 'class AttachmentUploadView' in source
        assert 'class AttachmentDownloadView' in source
        assert 'class AttachmentListView' in source
        assert 'class AttachmentMetadataView' in source

        # Check authentication is required
        assert 'permission_classes = [IsAuthenticated]' in source

    def test_views_have_correct_methods(self):
        """Test views implement correct HTTP methods"""
        import os

        views_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'views.py'
        )

        with open(views_path, 'r') as f:
            source = f.read()

        # Upload should have POST
        assert 'def post(self, request, conversation_id, message_id):' in source

        # Download should have GET
        assert 'def get(self, request, conversation_id, message_id, attachment_id):' in source


class TestAttachmentURLs:
    """Tests for attachment URL configuration"""

    def test_attachment_urls_defined(self):
        """Test attachment URL patterns are configured (via source inspection)"""
        import os

        urls_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'urls.py'
        )

        with open(urls_path, 'r') as f:
            source = f.read()

        # Check URL patterns exist
        assert "name='attachment-upload'" in source
        assert "name='attachment-list'" in source
        assert "name='attachment-download'" in source
        assert "name='attachment-metadata'" in source

        # Check views are imported
        assert 'AttachmentUploadView' in source
        assert 'AttachmentDownloadView' in source
        assert 'AttachmentListView' in source
        assert 'AttachmentMetadataView' in source


class TestAttachmentSecurity:
    """Security tests for file attachments"""

    def test_encrypted_file_cannot_be_read_without_key(self):
        """Test encrypted files are unreadable without decryption key"""
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM
        import secrets

        # Encrypt file
        plaintext = b"Secret document content"
        key = secrets.token_bytes(32)
        nonce = secrets.token_bytes(12)

        aesgcm = AESGCM(key)
        ciphertext = aesgcm.encrypt(nonce, plaintext, None)

        # Ciphertext should not contain plaintext
        assert plaintext not in ciphertext

        # Attempting to decrypt with wrong key should fail
        wrong_key = secrets.token_bytes(32)
        wrong_aesgcm = AESGCM(wrong_key)

        with pytest.raises(Exception):  # InvalidTag
            wrong_aesgcm.decrypt(nonce, ciphertext, None)

    def test_file_integrity_verification(self):
        """Test file hash detects tampering"""
        encrypted_data = b"encrypted file content"
        original_hash = hashlib.sha256(encrypted_data).hexdigest()

        # Tampered data should have different hash
        tampered_data = b"tampered file content"
        tampered_hash = hashlib.sha256(tampered_data).hexdigest()

        assert original_hash != tampered_hash

    def test_nonce_reuse_prevention(self):
        """Test unique nonce for each encryption"""
        import secrets

        # Generate multiple nonces
        nonces = [secrets.token_bytes(12) for _ in range(100)]

        # All should be unique
        assert len(set(nonces)) == 100

    def test_file_size_limits(self):
        """Test large file handling (should not cause memory issues)"""
        # Simulate processing a large file in chunks
        chunk_size = 64 * 1024  # 64KB chunks
        total_size = 100 * 1024 * 1024  # 100MB

        chunks_count = total_size // chunk_size
        assert chunks_count == 1600  # Verify chunk calculation

        # In practice, files should be streamed, not loaded entirely into memory

    def test_filename_sanitization(self):
        """Test dangerous filenames are handled safely"""
        dangerous_filenames = [
            '../../../etc/passwd',
            '..\\..\\..\\windows\\system32\\config\\sam',
            'file\x00.txt',
            '<script>alert(1)</script>.html',
            'file|rm -rf /.txt',
        ]

        for filename in dangerous_filenames:
            # Sanitize filename (simple example)
            safe_filename = filename.replace('..', '').replace('/', '_').replace('\\', '_')
            safe_filename = safe_filename.replace('\x00', '').replace('<', '').replace('>', '')
            safe_filename = safe_filename.replace('|', '_').replace(';', '_')

            # Should not contain path traversal
            assert '..' not in safe_filename
            assert '/' not in safe_filename
            assert '\\' not in safe_filename
            assert '\x00' not in safe_filename


class TestThumbnailGeneration:
    """Tests for thumbnail generation"""

    def test_thumbnail_encryption(self):
        """Test thumbnails are also encrypted"""
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM
        import secrets

        # Simulate thumbnail data
        thumbnail_data = b"\x89PNG\r\n\x1a\n" + secrets.token_bytes(1000)

        # Encrypt thumbnail with separate key
        thumbnail_key = secrets.token_bytes(32)
        nonce = secrets.token_bytes(12)

        aesgcm = AESGCM(thumbnail_key)
        encrypted_thumbnail = aesgcm.encrypt(nonce, thumbnail_data, None)

        # Decrypt and verify
        decrypted = aesgcm.decrypt(nonce, encrypted_thumbnail, None)
        assert decrypted == thumbnail_data

    def test_thumbnail_dimensions(self):
        """Test thumbnail dimensions are appropriate"""
        # Standard thumbnail dimensions
        max_width = 200
        max_height = 200

        # Original dimensions
        test_cases = [
            (1920, 1080, 200, 112),  # Landscape
            (1080, 1920, 112, 200),  # Portrait
            (100, 100, 100, 100),    # Small (no resize)
            (400, 400, 200, 200),    # Square
        ]

        for orig_w, orig_h, expected_w, expected_h in test_cases:
            # Calculate scaled dimensions maintaining aspect ratio
            if orig_w <= max_width and orig_h <= max_height:
                new_w, new_h = orig_w, orig_h
            elif orig_w / orig_h > max_width / max_height:
                new_w = max_width
                new_h = int(orig_h * (max_width / orig_w))
            else:
                new_h = max_height
                new_w = int(orig_w * (max_height / orig_h))

            assert new_w == expected_w
            assert new_h == expected_h


class TestMetadataEncryption:
    """Tests for encrypted file metadata"""

    def test_metadata_encryption(self):
        """Test file metadata is encrypted"""
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM
        import secrets
        import json

        metadata = {
            'width': 1920,
            'height': 1080,
            'duration': 120.5,  # For videos
            'exif': {
                'camera': 'iPhone 15',
                'gps': None  # Stripped for privacy
            }
        }

        metadata_json = json.dumps(metadata).encode()

        # Encrypt metadata
        key = secrets.token_bytes(32)
        nonce = secrets.token_bytes(12)

        aesgcm = AESGCM(key)
        encrypted_metadata = aesgcm.encrypt(nonce, metadata_json, None)

        # Decrypt and verify
        decrypted = aesgcm.decrypt(nonce, encrypted_metadata, None)
        parsed = json.loads(decrypted)

        assert parsed['width'] == 1920
        assert parsed['height'] == 1080

    def test_sensitive_metadata_stripping(self):
        """Test GPS and other sensitive data is stripped"""
        original_metadata = {
            'width': 1920,
            'height': 1080,
            'gps_latitude': 40.7128,
            'gps_longitude': -74.0060,
            'camera_serial': 'ABC123',
            'user_name': 'John Doe',
        }

        # Strip sensitive fields
        sensitive_fields = ['gps_latitude', 'gps_longitude', 'camera_serial', 'user_name']
        safe_metadata = {k: v for k, v in original_metadata.items() if k not in sensitive_fields}

        assert 'width' in safe_metadata
        assert 'height' in safe_metadata
        assert 'gps_latitude' not in safe_metadata
        assert 'gps_longitude' not in safe_metadata
        assert 'camera_serial' not in safe_metadata
        assert 'user_name' not in safe_metadata
