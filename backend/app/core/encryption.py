"""
Encryption utilities for sensitive data (API keys).

Uses Fernet symmetric encryption from cryptography library.
"""
from cryptography.fernet import Fernet, InvalidToken

from app.config import settings


def get_fernet() -> Fernet:
    """Get Fernet instance with configured encryption key."""
    key = settings.encryption_key
    # Ensure key is proper base64-encoded 32-byte key
    if not key or len(key) < 32:
        raise ValueError(
            "ENCRYPTION_KEY must be a valid Fernet key. "
            "Generate with: python -c \"from cryptography.fernet import Fernet; "
            "print(Fernet.generate_key().decode())\""
        )
    return Fernet(key.encode())


def encrypt_api_key(api_key: str) -> str:
    """
    Encrypt an API key for secure storage.

    Args:
        api_key: Plain text API key

    Returns:
        Encrypted API key as base64-encoded string
    """
    if not api_key:
        raise ValueError("API key cannot be empty")
    f = get_fernet()
    encrypted = f.encrypt(api_key.encode())
    return encrypted.decode()


def decrypt_api_key(encrypted_key: str) -> str:
    """
    Decrypt an encrypted API key.

    Args:
        encrypted_key: Fernet-encrypted API key

    Returns:
        Plain text API key

    Raises:
        ValueError: If decryption fails (invalid key or corrupted data)
    """
    if not encrypted_key:
        raise ValueError("Encrypted key cannot be empty")
    try:
        f = get_fernet()
        decrypted = f.decrypt(encrypted_key.encode())
        return decrypted.decode()
    except InvalidToken as e:
        raise ValueError(f"Failed to decrypt API key: {e}") from e


def mask_api_key(api_key: str, visible_chars: int = 4) -> str:
    """
    Mask an API key for display, showing only last few characters.

    Args:
        api_key: Plain text API key
        visible_chars: Number of characters to show at the end

    Returns:
        Masked API key like "sk-...xxxx"
    """
    if not api_key:
        return ""
    if len(api_key) <= visible_chars:
        return "*" * len(api_key)

    # Extract prefix (e.g., "sk-" for OpenAI)
    prefix = ""
    if api_key.startswith("sk-"):
        prefix = "sk-"
    elif api_key.startswith("AIza"):
        prefix = "AIza"

    suffix = api_key[-visible_chars:]
    return f"{prefix}...{suffix}"
