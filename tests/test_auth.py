import pytest
from web.auth import hash_password, verify_password, create_access_token, decode_token


class TestAuth:
    def test_hash_and_verify_password(self):
        pw = "TestPassword123!"
        hashed = hash_password(pw)
        assert hashed != pw
        assert verify_password(pw, hashed) is True

    def test_verify_wrong_password(self):
        hashed = hash_password("correct")
        assert verify_password("wrong", hashed) is False

    def test_create_and_decode_token(self):
        token = create_access_token(user_id=1, email="test@test.com", is_admin=True)
        payload = decode_token(token)
        assert payload["sub"] == "1"
        assert payload["email"] == "test@test.com"
        assert payload["admin"] is True

    def test_invalid_token(self):
        with pytest.raises(Exception):
            decode_token("invalid.token.here")
