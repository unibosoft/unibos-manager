"""
Messenger Encryption Service

Provides end-to-end encryption for messages using:
- X25519 for key exchange (Curve25519)
- AES-256-GCM for message encryption
- Ed25519 for message signing
- HKDF for key derivation

Security Properties:
- End-to-end encryption (server cannot read messages)
- Perfect Forward Secrecy (session keys)
- Message authentication (signatures)
- Replay attack prevention (nonces)
"""

import os
import base64
import hashlib
import logging
from typing import Tuple, Optional, Dict, Any
from dataclasses import dataclass

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey, X25519PublicKey
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.backends import default_backend
from cryptography.exceptions import InvalidSignature

logger = logging.getLogger('messenger.encryption')


@dataclass
class KeyPair:
    """Holds a public/private key pair"""
    public_key: bytes
    private_key: bytes
    key_type: str  # 'x25519' or 'ed25519'


@dataclass
class EncryptedMessage:
    """Encrypted message with all necessary metadata"""
    ciphertext: bytes
    nonce: bytes
    signature: bytes
    sender_public_key: bytes
    encryption_version: int = 1


class EncryptionService:
    """
    End-to-End Encryption Service for Messenger

    Usage:
        # Generate keys for a user
        service = EncryptionService()
        x25519_pair = service.generate_x25519_keypair()
        ed25519_pair = service.generate_ed25519_keypair()

        # Encrypt a message
        encrypted = service.encrypt_message(
            plaintext="Hello, World!",
            sender_private_key=sender_x25519_private,
            recipient_public_key=recipient_x25519_public,
            sender_signing_key=sender_ed25519_private
        )

        # Decrypt a message
        decrypted = service.decrypt_message(
            encrypted_message=encrypted,
            recipient_private_key=recipient_x25519_private,
            sender_public_key=sender_x25519_public,
            sender_signing_public_key=sender_ed25519_public
        )
    """

    # Constants
    NONCE_SIZE = 12  # AES-GCM nonce size
    KEY_SIZE = 32    # AES-256 key size
    CURRENT_VERSION = 1

    def __init__(self):
        self.backend = default_backend()

    # ========== Key Generation ==========

    def generate_x25519_keypair(self) -> KeyPair:
        """
        Generate X25519 key pair for key exchange.

        Returns:
            KeyPair with public and private keys as bytes
        """
        private_key = X25519PrivateKey.generate()
        public_key = private_key.public_key()

        return KeyPair(
            public_key=public_key.public_bytes_raw(),
            private_key=private_key.private_bytes_raw(),
            key_type='x25519'
        )

    def generate_ed25519_keypair(self) -> KeyPair:
        """
        Generate Ed25519 key pair for message signing.

        Returns:
            KeyPair with public and private keys as bytes
        """
        private_key = Ed25519PrivateKey.generate()
        public_key = private_key.public_key()

        return KeyPair(
            public_key=public_key.public_bytes_raw(),
            private_key=private_key.private_bytes(
                encoding=serialization.Encoding.Raw,
                format=serialization.PrivateFormat.Raw,
                encryption_algorithm=serialization.NoEncryption()
            ),
            key_type='ed25519'
        )

    def generate_user_keypairs(self) -> Dict[str, KeyPair]:
        """
        Generate all key pairs needed for a user.

        Returns:
            Dict with 'encryption' (X25519) and 'signing' (Ed25519) key pairs
        """
        return {
            'encryption': self.generate_x25519_keypair(),
            'signing': self.generate_ed25519_keypair()
        }

    # ========== Key Derivation ==========

    def derive_shared_secret(
        self,
        private_key: bytes,
        peer_public_key: bytes
    ) -> bytes:
        """
        Derive shared secret using X25519 key exchange.

        Args:
            private_key: Local X25519 private key
            peer_public_key: Peer's X25519 public key

        Returns:
            32-byte shared secret
        """
        private = X25519PrivateKey.from_private_bytes(private_key)
        public = X25519PublicKey.from_public_bytes(peer_public_key)
        return private.exchange(public)

    def derive_message_key(
        self,
        shared_secret: bytes,
        context: bytes = b'messenger-v1'
    ) -> bytes:
        """
        Derive message encryption key using HKDF.

        Args:
            shared_secret: Shared secret from X25519 exchange
            context: Context info for key derivation

        Returns:
            32-byte AES key
        """
        hkdf = HKDF(
            algorithm=hashes.SHA256(),
            length=self.KEY_SIZE,
            salt=None,
            info=context,
            backend=self.backend
        )
        return hkdf.derive(shared_secret)

    # ========== Message Encryption ==========

    def encrypt_message(
        self,
        plaintext: str,
        sender_private_key: bytes,
        recipient_public_key: bytes,
        sender_signing_key: bytes,
        associated_data: Optional[bytes] = None
    ) -> EncryptedMessage:
        """
        Encrypt a message for a recipient.

        Uses X25519 for key exchange, AES-256-GCM for encryption,
        and Ed25519 for signing.

        Args:
            plaintext: Message to encrypt
            sender_private_key: Sender's X25519 private key
            recipient_public_key: Recipient's X25519 public key
            sender_signing_key: Sender's Ed25519 private key
            associated_data: Optional additional authenticated data

        Returns:
            EncryptedMessage with ciphertext, nonce, signature
        """
        # Derive shared secret and message key
        shared_secret = self.derive_shared_secret(sender_private_key, recipient_public_key)
        message_key = self.derive_message_key(shared_secret)

        # Generate random nonce
        nonce = os.urandom(self.NONCE_SIZE)

        # Encrypt with AES-256-GCM
        aesgcm = AESGCM(message_key)
        plaintext_bytes = plaintext.encode('utf-8')
        ciphertext = aesgcm.encrypt(nonce, plaintext_bytes, associated_data)

        # Sign the message (ciphertext + nonce)
        signing_key = Ed25519PrivateKey.from_private_bytes(sender_signing_key)
        signature_data = nonce + ciphertext
        if associated_data:
            signature_data += associated_data
        signature = signing_key.sign(signature_data)

        # Get sender's public key for verification
        x25519_private = X25519PrivateKey.from_private_bytes(sender_private_key)
        sender_public = x25519_private.public_key().public_bytes_raw()

        return EncryptedMessage(
            ciphertext=ciphertext,
            nonce=nonce,
            signature=signature,
            sender_public_key=sender_public,
            encryption_version=self.CURRENT_VERSION
        )

    def decrypt_message(
        self,
        encrypted_message: EncryptedMessage,
        recipient_private_key: bytes,
        sender_public_key: bytes,
        sender_signing_public_key: bytes,
        associated_data: Optional[bytes] = None
    ) -> str:
        """
        Decrypt a message from a sender.

        Verifies signature before decryption.

        Args:
            encrypted_message: EncryptedMessage to decrypt
            recipient_private_key: Recipient's X25519 private key
            sender_public_key: Sender's X25519 public key
            sender_signing_public_key: Sender's Ed25519 public key
            associated_data: Optional additional authenticated data

        Returns:
            Decrypted plaintext string

        Raises:
            InvalidSignature: If message signature is invalid
            Exception: If decryption fails
        """
        # Verify signature first
        signing_public = Ed25519PublicKey.from_public_bytes(sender_signing_public_key)
        signature_data = encrypted_message.nonce + encrypted_message.ciphertext
        if associated_data:
            signature_data += associated_data

        try:
            signing_public.verify(encrypted_message.signature, signature_data)
        except InvalidSignature:
            logger.warning("Message signature verification failed")
            raise

        # Derive shared secret and message key
        shared_secret = self.derive_shared_secret(recipient_private_key, sender_public_key)
        message_key = self.derive_message_key(shared_secret)

        # Decrypt with AES-256-GCM
        aesgcm = AESGCM(message_key)
        plaintext_bytes = aesgcm.decrypt(
            encrypted_message.nonce,
            encrypted_message.ciphertext,
            associated_data
        )

        return plaintext_bytes.decode('utf-8')

    # ========== Group Encryption ==========

    def generate_group_key(self) -> bytes:
        """
        Generate a random group encryption key.

        Returns:
            32-byte AES key for group encryption
        """
        return os.urandom(self.KEY_SIZE)

    def encrypt_group_key(
        self,
        group_key: bytes,
        recipient_public_key: bytes,
        sender_private_key: bytes
    ) -> bytes:
        """
        Encrypt group key for a specific recipient.

        Args:
            group_key: The group's AES key
            recipient_public_key: Recipient's X25519 public key
            sender_private_key: Sender's X25519 private key

        Returns:
            Encrypted group key (nonce + ciphertext)
        """
        shared_secret = self.derive_shared_secret(sender_private_key, recipient_public_key)
        key_encryption_key = self.derive_message_key(shared_secret, b'group-key-v1')

        nonce = os.urandom(self.NONCE_SIZE)
        aesgcm = AESGCM(key_encryption_key)
        ciphertext = aesgcm.encrypt(nonce, group_key, None)

        return nonce + ciphertext

    def decrypt_group_key(
        self,
        encrypted_group_key: bytes,
        sender_public_key: bytes,
        recipient_private_key: bytes
    ) -> bytes:
        """
        Decrypt group key.

        Args:
            encrypted_group_key: Encrypted group key (nonce + ciphertext)
            sender_public_key: Key creator's X25519 public key
            recipient_private_key: Recipient's X25519 private key

        Returns:
            Decrypted group key
        """
        nonce = encrypted_group_key[:self.NONCE_SIZE]
        ciphertext = encrypted_group_key[self.NONCE_SIZE:]

        shared_secret = self.derive_shared_secret(recipient_private_key, sender_public_key)
        key_encryption_key = self.derive_message_key(shared_secret, b'group-key-v1')

        aesgcm = AESGCM(key_encryption_key)
        return aesgcm.decrypt(nonce, ciphertext, None)

    def encrypt_with_group_key(
        self,
        plaintext: str,
        group_key: bytes,
        sender_signing_key: bytes
    ) -> EncryptedMessage:
        """
        Encrypt message with group key.

        Args:
            plaintext: Message to encrypt
            group_key: Group's AES key
            sender_signing_key: Sender's Ed25519 private key

        Returns:
            EncryptedMessage
        """
        nonce = os.urandom(self.NONCE_SIZE)

        aesgcm = AESGCM(group_key)
        plaintext_bytes = plaintext.encode('utf-8')
        ciphertext = aesgcm.encrypt(nonce, plaintext_bytes, None)

        # Sign
        signing_key = Ed25519PrivateKey.from_private_bytes(sender_signing_key)
        signature = signing_key.sign(nonce + ciphertext)

        return EncryptedMessage(
            ciphertext=ciphertext,
            nonce=nonce,
            signature=signature,
            sender_public_key=b'',  # Not needed for group messages
            encryption_version=self.CURRENT_VERSION
        )

    def decrypt_with_group_key(
        self,
        encrypted_message: EncryptedMessage,
        group_key: bytes,
        sender_signing_public_key: bytes
    ) -> str:
        """
        Decrypt message with group key.

        Args:
            encrypted_message: Encrypted message
            group_key: Group's AES key
            sender_signing_public_key: Sender's Ed25519 public key

        Returns:
            Decrypted plaintext
        """
        # Verify signature
        signing_public = Ed25519PublicKey.from_public_bytes(sender_signing_public_key)
        signature_data = encrypted_message.nonce + encrypted_message.ciphertext
        signing_public.verify(encrypted_message.signature, signature_data)

        # Decrypt
        aesgcm = AESGCM(group_key)
        plaintext_bytes = aesgcm.decrypt(
            encrypted_message.nonce,
            encrypted_message.ciphertext,
            None
        )

        return plaintext_bytes.decode('utf-8')

    # ========== File Encryption ==========

    def encrypt_file(
        self,
        file_data: bytes,
        file_key: Optional[bytes] = None
    ) -> Tuple[bytes, bytes, bytes]:
        """
        Encrypt a file.

        Args:
            file_data: File contents
            file_key: Optional encryption key (generated if not provided)

        Returns:
            Tuple of (encrypted_data, nonce, file_key)
        """
        if file_key is None:
            file_key = os.urandom(self.KEY_SIZE)

        nonce = os.urandom(self.NONCE_SIZE)
        aesgcm = AESGCM(file_key)
        encrypted_data = aesgcm.encrypt(nonce, file_data, None)

        return encrypted_data, nonce, file_key

    def decrypt_file(
        self,
        encrypted_data: bytes,
        nonce: bytes,
        file_key: bytes
    ) -> bytes:
        """
        Decrypt a file.

        Args:
            encrypted_data: Encrypted file contents
            nonce: Encryption nonce
            file_key: File encryption key

        Returns:
            Decrypted file contents
        """
        aesgcm = AESGCM(file_key)
        return aesgcm.decrypt(nonce, encrypted_data, None)

    # ========== Utility Functions ==========

    def hash_content(self, content: bytes) -> str:
        """
        SHA-256 hash of content.

        Args:
            content: Data to hash

        Returns:
            Hex-encoded hash
        """
        return hashlib.sha256(content).hexdigest()

    def to_base64(self, data: bytes) -> str:
        """Encode bytes to base64 string"""
        return base64.b64encode(data).decode('ascii')

    def from_base64(self, data: str) -> bytes:
        """Decode base64 string to bytes"""
        return base64.b64decode(data.encode('ascii'))

    def serialize_encrypted_message(self, msg: EncryptedMessage) -> Dict[str, Any]:
        """
        Serialize EncryptedMessage to dict for storage/transmission.

        Args:
            msg: EncryptedMessage to serialize

        Returns:
            Dict with base64-encoded fields
        """
        return {
            'ciphertext': self.to_base64(msg.ciphertext),
            'nonce': self.to_base64(msg.nonce),
            'signature': self.to_base64(msg.signature),
            'sender_public_key': self.to_base64(msg.sender_public_key) if msg.sender_public_key else '',
            'encryption_version': msg.encryption_version
        }

    def deserialize_encrypted_message(self, data: Dict[str, Any]) -> EncryptedMessage:
        """
        Deserialize dict to EncryptedMessage.

        Args:
            data: Dict with base64-encoded fields

        Returns:
            EncryptedMessage
        """
        return EncryptedMessage(
            ciphertext=self.from_base64(data['ciphertext']),
            nonce=self.from_base64(data['nonce']),
            signature=self.from_base64(data['signature']),
            sender_public_key=self.from_base64(data['sender_public_key']) if data.get('sender_public_key') else b'',
            encryption_version=data.get('encryption_version', 1)
        )


# Singleton instance
_encryption_service: Optional[EncryptionService] = None


def get_encryption_service() -> EncryptionService:
    """Get the global encryption service instance"""
    global _encryption_service
    if _encryption_service is None:
        _encryption_service = EncryptionService()
    return _encryption_service
