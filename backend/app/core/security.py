"""JWT auth + RBAC (roles: admin, scientist, viewer)."""

from datetime import UTC, datetime, timedelta
from enum import Enum
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import get_settings

pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")
bearer = HTTPBearer(auto_error=False)
settings = get_settings()


class Role(str, Enum):
    ADMIN = "admin"
    SCIENTIST = "scientist"
    VIEWER = "viewer"


def hash_password(pw: str) -> str:
    return pwd_ctx.hash(pw)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_ctx.verify(plain, hashed)


def create_access_token(sub: str, role: str = Role.SCIENTIST.value) -> str:
    exp = datetime.now(UTC) + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    return jwt.encode(
        {"sub": sub, "role": role, "exp": exp},
        settings.JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM,
    )


def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
    except JWTError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from e


def get_current_user(
    creds: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)],
) -> dict:
    # Demo mode: allow anonymous viewer so judges can click without signup.
    if creds is None:
        return {"sub": "anonymous", "role": Role.VIEWER.value}
    payload = decode_token(creds.credentials)
    return {
        "sub": payload.get("sub", "unknown"),
        "role": payload.get("role", Role.VIEWER.value),
    }


def require_roles(*roles: Role):
    def _guard(user: Annotated[dict, Depends(get_current_user)]) -> dict:
        if user["role"] not in [r.value for r in roles] and user["role"] != Role.ADMIN.value:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient role")
        return user

    return _guard
