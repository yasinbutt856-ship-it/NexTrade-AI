import os
from cryptography.fernet import Fernet

_CIPHER = None


def _get_cipher():
    global _CIPHER
    if _CIPHER is None:
        key = os.getenv("ENCRYPTION_KEY")
        if not key:
            key = Fernet.generate_key().decode()
        if isinstance(key, str):
            key = key.encode()
        if len(key) != 44:
            key = Fernet.generate_key()
        _CIPHER = Fernet(key)
    return _CIPHER


def encrypt(val: str) -> str:
    return _get_cipher().encrypt(val.encode()).decode()


def decrypt(val: str) -> str:
    return _get_cipher().decrypt(val.encode()).decode()
