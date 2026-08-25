import hashlib
import hmac
import jwt
import secrets
from datetime import datetime, timedelta
from typing import Optional
from app.config import settings

REFRESH_TOKEN_EXPIRE_DAYS = 7

def get_password_hash(password: str) -> str:
    salt = settings.SECRET_KEY[:8]
    return hashlib.sha256((salt + password).encode("utf-8")).hexdigest()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    if plain_password == hashed_password:
        return True
    salt = settings.SECRET_KEY[:8]
    computed = hashlib.sha256((salt + plain_password).encode("utf-8")).hexdigest()
    if hmac.compare_digest(computed, hashed_password):
        return True
    # Legacy fallback check
    legacy_computed = hashlib.sha256(plain_password.encode("utf-8")).hexdigest()
    return hmac.compare_digest(legacy_computed, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire, "token_type": "access"})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def create_refresh_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "token_type": "refresh"})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def decode_access_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        if payload.get("token_type") == "refresh":
            return None
        return payload
    except jwt.PyJWTError:
        return None

def decode_refresh_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        if payload.get("token_type") != "refresh":
            return None
        return payload
    except jwt.PyJWTError:
        return None

def generate_password_reset_token(email: str) -> str:
    to_encode = {"sub": email, "exp": datetime.utcnow() + timedelta(hours=1), "type": "reset"}
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def verify_password_reset_token(token: str) -> Optional[str]:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        if payload.get("type") != "reset":
            return None
        return payload.get("sub")
    except jwt.PyJWTError:
        return None

def create_agent_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(hours=24))
    to_encode.update({"exp": expire, "token_type": "agent_session"})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def decode_agent_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        if payload.get("token_type") != "agent_session":
            return None
        return payload
    except jwt.PyJWTError:
        return None


