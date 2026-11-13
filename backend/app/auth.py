# backend/app/auth.py
import os
import time
from datetime import datetime, timedelta
from typing import Optional

import jwt  # PyJWT (already installed)
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer

from .config import JWT_SECRET_KEY, ACCESS_TOKEN_EXPIRE_MINUTES

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm="HS256")
    return encoded_jwt

def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.InvalidTokenError:
        return None

import hashlib
import os
import time
from datetime import datetime, timedelta
from typing import Optional

import jwt  # PyJWT (already installed)
from fastapi.security import OAuth2PasswordBearer

from .config import JWT_SECRET_KEY, ACCESS_TOKEN_EXPIRE_MINUTES

def _hash_password(password: str, salt: bytes) -> str:
    """Hash a password with SHA-256 using the provided salt.
    Returns hex digest of salt + hash.
    """
    dk = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100_000)
    return salt.hex() + dk.hex()

def _verify_password(plain_password: str, stored_hash: str) -> bool:
    """Verify password against stored hash (salt+hash)."""
    salt_hex = stored_hash[:32]  # first 16 bytes (32 hex chars)
    salt = bytes.fromhex(salt_hex)
    expected = _hash_password(plain_password, salt)
    return expected == stored_hash

def get_password_hash(password: str) -> str:
    # Generate a random 16‑byte salt
    salt = os.urandom(16)
    return _hash_password(password, salt)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return _verify_password(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm="HS256")
    return encoded_jwt

def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.InvalidTokenError:
        return None

# OAuth2 scheme for extracting bearer token from Authorization header
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")



