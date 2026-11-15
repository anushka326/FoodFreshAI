# backend/app/auth.py
"""
FoodFresh AI - Authentication Utilities (Compatibility Module)
Provides password hashing, verification, and JWT access token handling.
"""
import base64
import hashlib
import json
import os
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional

try:
    import jwt
except ImportError:
    jwt = None

from fastapi.security import OAuth2PasswordBearer
from .config import JWT_SECRET_KEY, ACCESS_TOKEN_EXPIRE_MINUTES

SECRET_KEY = JWT_SECRET_KEY or os.getenv("JWT_SECRET", "foodfresh-jwt-secret-key-prod-2026")
ALGORITHM = "HS256"

def _hash_password(password: str, salt: bytes) -> str:
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100_000)
    return salt.hex() + dk.hex()

def get_password_hash(password: str) -> str:
    salt = os.urandom(16)
    return _hash_password(password, salt)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    if not hashed_password or len(hashed_password) < 32:
        return False
    try:
        salt_hex = hashed_password[:32]
        salt = bytes.fromhex(salt_hex)
        expected = _hash_password(plain_password, salt)
        return secrets.compare_digest(expected, hashed_password)
    except Exception:
        return False

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire.timestamp() if jwt is None else expire})

    if jwt is not None:
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    # Built-in lightweight signed token fallback if PyJWT is not installed
    encoded = base64.urlsafe_b64encode(json.dumps(to_encode).encode()).decode()
    sig = hashlib.sha256(f"{encoded}.{SECRET_KEY}".encode()).hexdigest()
    return f"{encoded}.{sig}"

def decode_access_token(token: str) -> Optional[dict]:
    if jwt is not None:
        try:
            return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        except Exception:
            return None

    # Built-in lightweight token decoder
    try:
        parts = token.split(".")
        if len(parts) != 2:
            return None
        encoded, sig = parts
        expected_sig = hashlib.sha256(f"{encoded}.{SECRET_KEY}".encode()).hexdigest()
        if not secrets.compare_digest(sig, expected_sig):
            return None
        payload = json.loads(base64.urlsafe_b64decode(encoded.encode()).decode())
        if payload.get("exp") and payload["exp"] < datetime.now(timezone.utc).timestamp():
            return None
        return payload
    except Exception:
        return None

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")
