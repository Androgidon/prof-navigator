from datetime import timedelta

import pytest

from app.services.auth_service import AuthService


def test_hash_and_verify_password():
    raw = "StrongPass123"
    hashed = AuthService.hash_password(raw)
    assert hashed != raw
    assert AuthService.verify_password(raw, hashed)
    assert not AuthService.verify_password("wrong", hashed)


def test_tokens_round_trip():
    access = AuthService.create_access_token("user-123")
    refresh = AuthService.create_refresh_token("user-123", "refresh-uuid")
    payload = AuthService.token_payload(access)
    assert payload is not None
    assert payload["sub"] == "user-123"
    assert AuthService.token_expiration(payload) is not None
    refresh_payload = AuthService.token_payload(refresh)
    assert refresh_payload is not None
    assert refresh_payload["jti"] == "refresh-uuid"
    assert refresh_payload["type"] == "refresh"
    assert AuthService.token_expiration(refresh_payload) > AuthService.token_expiration(payload)


def test_token_payload_invalid():
    assert AuthService.token_payload("invalid") is None
    assert AuthService.token_expiration(None) is None
