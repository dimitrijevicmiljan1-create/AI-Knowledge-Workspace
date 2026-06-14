from cryptography.fernet import Fernet, InvalidToken

from app.core.config import settings


class TokenEncryptionError(Exception):
    pass


class TokenEncryption:
    """Encrypt and decrypt sensitive tokens at rest."""

    def __init__(self, key: str | None = None) -> None:
        encryption_key = key or settings.github_token_encryption_key
        if not encryption_key:
            raise TokenEncryptionError("GitHub token encryption key is not configured")
        try:
            self._fernet = Fernet(encryption_key.encode() if isinstance(encryption_key, str) else encryption_key)
        except Exception as error:
            raise TokenEncryptionError("Invalid GitHub token encryption key") from error

    def encrypt(self, token: str) -> str:
        return self._fernet.encrypt(token.encode()).decode()

    def decrypt(self, encrypted_token: str) -> str:
        try:
            return self._fernet.decrypt(encrypted_token.encode()).decode()
        except InvalidToken as error:
            raise TokenEncryptionError("Failed to decrypt token") from error


def get_token_encryption() -> TokenEncryption:
    return TokenEncryption()
