import hmac
import hashlib
from datetime import datetime, timedelta, timezone
from typing import Optional
import jwt
import bcrypt
from backend.config import settings

def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against its bcrypt hash."""
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8")
    )

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a signed JWT access token."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta if expires_delta
        else timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)

def verify_access_token(token: str) -> Optional[dict]:
    """Decode and validate a JWT. Returns payload dict or None on failure."""
    try:
        return jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
    except jwt.PyJWTError:
        return None

def generate_qr_signature(table_id: str) -> str:
    """Generate a 16-char HMAC-SHA256 signature for a table ID."""
    return hmac.new(
        settings.QR_SECRET.encode(),
        str(table_id).encode(),
        hashlib.sha256
    ).hexdigest()[:16]

def verify_qr_signature(table_id: str, sig: str) -> bool:
    """Verify the QR signature hasn't been tampered with."""
    if not sig:
        return False
    expected = generate_qr_signature(str(table_id))
    return hmac.compare_digest(expected, sig)
