import base64
import hashlib
import os

from cryptography.fernet import Fernet
from sqlalchemy.types import Text, TypeDecorator


def _build_fernet_key() -> bytes:
    raw = os.getenv('DATA_ENCRYPTION_KEY') or os.getenv('SECRET_KEY') or 'dev-secret'
    digest = hashlib.sha256(raw.encode('utf-8')).digest()
    return base64.urlsafe_b64encode(digest)


def get_fernet() -> Fernet:
    return Fernet(_build_fernet_key())


class EncryptedString(TypeDecorator):
    impl = Text
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        text = str(value)
        if not text:
            return text
        token = get_fernet().encrypt(text.encode('utf-8'))
        return token.decode('utf-8')

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        text = str(value)
        if not text:
            return text
        # Backward compatibility: keep working with existing plaintext rows.
        try:
            decrypted = get_fernet().decrypt(text.encode('utf-8'))
            return decrypted.decode('utf-8')
        except Exception:
            return text
