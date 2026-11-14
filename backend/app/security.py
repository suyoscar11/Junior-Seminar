from __future__ import annotations

import hashlib
import hmac
import secrets


def hash_password(password: str, salt: str | None = None) -> str:
    salt = salt or secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt), 210_000)
    return f"{salt}${digest.hex()}"


def verify_password(password: str, encoded: str) -> bool:
    salt, expected = encoded.split("$", 1)
    actual = hash_password(password, salt).split("$", 1)[1]
    return hmac.compare_digest(actual, expected)


def new_token() -> str:
    return secrets.token_urlsafe(32)

