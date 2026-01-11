"""
Security utilities for encryption and hashing.
SECURITY: Uses Fernet symmetric encryption for reversible secrets (like email passwords).
"""
import os
import base64
import hashlib
from cryptography.fernet import Fernet
import logging

logger = logging.getLogger(__name__)


def _get_or_create_key() -> bytes:
    """
    Get encryption key from environment or generate a new one.
    In production, ENCRYPTION_KEY should be set in environment variables!
    """
    key = os.getenv("ENCRYPTION_KEY")
    
    if key:
        # Validate key format
        try:
            # Key should be base64-encoded 32-byte key
            decoded = base64.urlsafe_b64decode(key)
            if len(decoded) == 32:
                return key.encode() if isinstance(key, str) else key
        except Exception:
            logger.warning("Invalid ENCRYPTION_KEY format, generating new key")
    
    # Generate key from a secret or create deterministic one for dev
    # WARNING: In production, always use a proper ENCRYPTION_KEY!
    secret = os.getenv("SUPABASE_KEY", "default-dev-secret")
    # Create a deterministic key from the secret (for dev consistency)
    key_bytes = hashlib.sha256(secret.encode()).digest()
    return base64.urlsafe_b64encode(key_bytes)


# Initialize Fernet cipher
_fernet: Fernet = None


def _get_fernet() -> Fernet:
    """Get or initialize Fernet cipher."""
    global _fernet
    if _fernet is None:
        key = _get_or_create_key()
        _fernet = Fernet(key)
    return _fernet


def encrypt_secret(plaintext: str) -> str:
    """
    Encrypt a secret (password, token, etc.) for storage.
    Returns base64-encoded encrypted string.
    """
    if not plaintext:
        return ""
    
    try:
        f = _get_fernet()
        encrypted = f.encrypt(plaintext.encode())
        return encrypted.decode()
    except Exception as e:
        logger.error(f"Encryption error: {e}")
        raise ValueError("Failed to encrypt secret")


def decrypt_secret(encrypted: str) -> str:
    """
    Decrypt a previously encrypted secret.
    Returns plaintext string.
    """
    if not encrypted:
        return ""
    
    try:
        f = _get_fernet()
        decrypted = f.decrypt(encrypted.encode())
        return decrypted.decode()
    except Exception as e:
        logger.error(f"Decryption error: {e}")
        raise ValueError("Failed to decrypt secret - key may have changed")


def is_encrypted(value: str) -> bool:
    """
    Check if a value appears to be Fernet-encrypted.
    Fernet tokens start with 'gAAAAA'.
    """
    if not value:
        return False
    return value.startswith("gAAAAA")
