import hashlib
import secrets
import uuid
from datetime import datetime, timedelta, timezone

import jwt
from passlib.context import CryptContext

from app.core.config import get_settings

settings = get_settings()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return pwd_context.verify(password, password_hash)


def hash_otp(code: str) -> str:
    return pwd_context.hash(code)


def verify_otp(code: str, code_hash: str) -> bool:
    return pwd_context.verify(code, code_hash)


def hash_lookup_token(token: str) -> str:
    """Deterministic hash for values that must be looked up by exact match
    (e.g. a password-reset token, which arrives with no other identifier to
    scope the query by). The token is high-entropy, so a fast hash is safe —
    unlike a password or OTP, brute-forcing the hash isn't feasible."""
    return hashlib.sha256(token.encode()).hexdigest()


def generate_otp(length: int | None = None) -> str:
    length = length or settings.otp_length
    return "".join(str(secrets.randbelow(10)) for _ in range(length))


def generate_reset_token() -> str:
    return secrets.token_urlsafe(32)


def create_access_token(*, subject: uuid.UUID, role: str) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(subject),
        "role": role,
        "type": "access",
        "iat": now,
        "exp": now + timedelta(minutes=settings.access_token_ttl_minutes),
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def create_refresh_token(*, subject: uuid.UUID, role: str) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(subject),
        "role": role,
        "type": "refresh",
        "iat": now,
        "exp": now + timedelta(days=settings.refresh_token_ttl_days),
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decode_token(token: str) -> dict:
    return jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
