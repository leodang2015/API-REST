from datetime import datetime, timedelta, timezone
from hashlib import sha256
from typing import Any
from uuid import uuid4

import jwt
from pwdlib import PasswordHash

from app.core.config import settings


password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    return password_hash.verify(password, hashed_password)


def create_token(
    subject: str,
    token_type: str,
    expires_delta: timedelta,
    *,
    token_id: str | None = None,
) -> str:
    now = datetime.now(timezone.utc)
    payload: dict[str, Any] = {
        "sub": subject,
        "type": token_type,
        "iat": now,
        "exp": now + expires_delta,
        "jti": token_id or str(uuid4()),
    }
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


def decode_token(token: str) -> dict[str, Any]:
    return jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])


def token_digest(token: str) -> str:
    return sha256(token.encode("utf-8")).hexdigest()


def token_expiration(token: str) -> datetime:
    claims = decode_token(token)
    expiration = claims.get("exp")
    if not isinstance(expiration, (int, float)):
        raise jwt.InvalidTokenError("Token sin expiración válida")
    return datetime.fromtimestamp(expiration, tz=timezone.utc)