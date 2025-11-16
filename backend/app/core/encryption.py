"""
Encryption Utilities

Provides Fernet encryption/decryption for sensitive data like Home Assistant access tokens.
"""
from cryptography.fernet import Fernet
from app.core.config import settings
import base64
import hashlib


def get_encryption_key() -> bytes:
    """
    Get or generate encryption key from settings.

    The key should be stored in ENCRYPTION_KEY environment variable.
    If not set, it will generate a key based on SECRET_KEY (not recommended for production).

    Returns:
        bytes: 32-byte encryption key suitable for Fernet
    """
    if hasattr(settings, 'ENCRYPTION_KEY') and settings.ENCRYPTION_KEY:
        # Use provided encryption key
        key = settings.ENCRYPTION_KEY.encode() if isinstance(settings.ENCRYPTION_KEY, str) else settings.ENCRYPTION_KEY

        # Ensure key is exactly 32 bytes (Fernet requirement)
        if len(key) != 32:
            # Hash the key to get exactly 32 bytes
            key = hashlib.sha256(key).digest()

        return base64.urlsafe_b64encode(key)

    # Fallback: derive from SECRET_KEY (not recommended for production)
    secret_key = settings.SECRET_KEY.encode()
    key_bytes = hashlib.sha256(secret_key).digest()
    return base64.urlsafe_b64encode(key_bytes)


def encrypt_value(value: str) -> str:
    """
    Encrypt a string value using Fernet symmetric encryption.

    Args:
        value: Plain text string to encrypt

    Returns:
        str: Encrypted value (base64 encoded)

    Example:
        >>> token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
        >>> encrypted = encrypt_value(token)
        >>> print(encrypted)  # "gAAAAABf..."
    """
    if not value:
        return ""

    key = get_encryption_key()
    fernet = Fernet(key)
    encrypted_bytes = fernet.encrypt(value.encode())
    return encrypted_bytes.decode()


def decrypt_value(encrypted_value: str) -> str:
    """
    Decrypt a Fernet-encrypted string value.

    Args:
        encrypted_value: Encrypted value (base64 encoded)

    Returns:
        str: Decrypted plain text string

    Raises:
        cryptography.fernet.InvalidToken: If decryption fails (wrong key or corrupted data)

    Example:
        >>> encrypted = "gAAAAABf..."
        >>> token = decrypt_value(encrypted)
        >>> print(token)  # "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    """
    if not encrypted_value:
        return ""

    key = get_encryption_key()
    fernet = Fernet(key)
    decrypted_bytes = fernet.decrypt(encrypted_value.encode())
    return decrypted_bytes.decode()


def mask_token(token: str, show_first: int = 2, show_last: int = 3) -> str:
    """
    Mask a token for display purposes.

    Args:
        token: Token to mask
        show_first: Number of characters to show at the beginning
        show_last: Number of characters to show at the end

    Returns:
        str: Masked token (e.g., "ey...abc")

    Example:
        >>> token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.abc123"
        >>> masked = mask_token(token)
        >>> print(masked)  # "ey...123"
    """
    if not token or len(token) <= (show_first + show_last):
        return "***"

    return f"{token[:show_first]}...{token[-show_last:]}"


def generate_encryption_key() -> str:
    """
    Generate a new random encryption key suitable for Fernet.

    Use this function to generate a key for ENCRYPTION_KEY environment variable.

    Returns:
        str: Base64-encoded 32-byte key

    Example:
        >>> key = generate_encryption_key()
        >>> print(f"ENCRYPTION_KEY={key}")
        # Add this to your .env file
    """
    key = Fernet.generate_key()
    return key.decode()


if __name__ == "__main__":
    # Generate a new encryption key for initial setup
    print("=" * 60)
    print("Fernet Encryption Key Generator")
    print("=" * 60)
    print("\nGenerated key (add this to your .env file):")
    print(f"\nENCRYPTION_KEY={generate_encryption_key()}")
    print("\n" + "=" * 60)
    print("Keep this key secret and never commit it to version control!")
    print("=" * 60)
