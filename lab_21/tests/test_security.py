"""Unit-тесты безопасности: хеширование паролей, JWT-токены, роли."""

import pytest

from restaurant.services.security import (
    create_access_token,
    decode_token,
    hash_password,
    role_from_token,
    verify_password,
)


class TestPasswordHashing:
    def test_hash_never_plain(self):
        hashed = hash_password("secret123")
        assert hashed != "secret123"
        assert hashed.startswith("$")

    def test_verify_correct_password(self):
        assert verify_password("secret123", hash_password("secret123")) is True

    def test_verify_wrong_password(self):
        assert verify_password("wrong", hash_password("secret123")) is False

    def test_two_hashes_differ(self):
        assert hash_password("secret123") != hash_password("secret123")


class TestJwt:
    def test_create_and_decode_roundtrip(self):
        token = create_access_token(42, "ADMIN")
        payload = decode_token(token)
        assert payload["sub"] == "42"
        assert payload["role"] == "ADMIN"

    def test_role_from_token(self):
        assert role_from_token(create_access_token(1, "USER")) == "USER"

    def test_decode_invalid_token_raises(self):
        with pytest.raises(ValueError):
            decode_token("not-a-valid-token")

    def test_decode_tampered_token_raises(self):
        token = create_access_token(1, "USER")
        with pytest.raises(ValueError):
            decode_token(token[:-2] + "xx")
