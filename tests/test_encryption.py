import pytest
from shared.encryption import encrypt, decrypt


class TestEncryption:
    def test_encrypt_decrypt(self):
        original = "my-secret-api-key-12345"
        encrypted = encrypt(original)
        assert encrypted != original
        decrypted = decrypt(encrypted)
        assert decrypted == original

    def test_encryption_determinism(self):
        val = "test-value"
        e1 = encrypt(val)
        e2 = encrypt(val)
        assert e1 != e2  # Fernet is not deterministic (different IV each time)

    def test_decrypt_invalid(self):
        with pytest.raises(Exception):
            decrypt("invalid-encrypted-data")

    def test_empty_string(self):
        original = ""
        encrypted = encrypt(original)
        decrypted = decrypt(encrypted)
        assert decrypted == original

    def test_special_chars(self):
        original = "!@#$%^&*()_+-=[]{}|;':\",./<>?`~ 你好"
        encrypted = encrypt(original)
        decrypted = decrypt(encrypted)
        assert decrypted == original
