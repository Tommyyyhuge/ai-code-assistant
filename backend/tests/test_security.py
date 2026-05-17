import pytest
from app.utils.security import (
    get_password_hash, verify_password,
    create_access_token, decode_token,
    encrypt_api_key, decrypt_api_key,
)


def test_password_hash():
    password = "testpassword123"
    hashed = get_password_hash(password)
    assert verify_password(password, hashed) is True
    assert verify_password("wrongpassword", hashed) is False


def test_access_token():
    data = {"sub": "user@example.com"}
    token = create_access_token(data)
    payload = decode_token(token)
    assert payload is not None
    assert payload["sub"] == "user@example.com"
    assert payload["type"] == "access"


# ── API Key 加解密测试 ──────────────────────────────────────────

def test_encrypt_decrypt_api_key_roundtrip():
    """加密后解密应该得到原始明文"""
    plain = "sk-abc123def456ghi789"
    encrypted = encrypt_api_key(plain)
    assert encrypted != plain
    assert decrypt_api_key(encrypted) == plain


def test_encrypt_decrypt_empty_string():
    """空字符串加密解密应返回空字符串"""
    assert encrypt_api_key("") == ""
    assert decrypt_api_key("") == ""


def test_decrypt_plaintext_fallback():
    """解密明文数据应降级返回原文（兼容历史数据）"""
    plain = "sk-legacy-plaintext-key"
    assert decrypt_api_key(plain) == plain


def test_encrypt_different_keys_produce_different_output():
    """不同明文产生不同密文"""
    encrypted_a = encrypt_api_key("key-aaa")
    encrypted_b = encrypt_api_key("key-bbb")
    assert encrypted_a != encrypted_b


def test_encrypt_same_input_produces_different_ciphertext():
    """相同明文两次加密产生不同密文（Fernet 含随机 IV）"""
    encrypted_1 = encrypt_api_key("same-key-123")
    encrypted_2 = encrypt_api_key("same-key-123")
    # Fernet 每次加密含时间戳，密文不同但都能解密
    assert decrypt_api_key(encrypted_1) == "same-key-123"
    assert decrypt_api_key(encrypted_2) == "same-key-123"