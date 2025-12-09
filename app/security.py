from typing import Any, Dict, Optional

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt import PyJWTError

from app.core.config import settings

oauth2_scheme: Optional[OAuth2PasswordBearer]

if settings.AUTH_ENABLED:
    oauth2_scheme = OAuth2PasswordBearer(
        tokenUrl=settings.OAUTH2_TOKEN_URL  # type: ignore[arg-type]
    )
else:
    oauth2_scheme = None  # type: ignore[assignment]


def decode_access_token(token: str) -> Dict[str, Any]:
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,  # guaranteed not None if AUTH_ENABLED=True
            algorithms=[settings.JWT_ALGORITHM],
        )
        return payload
    except PyJWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        ) from e


def get_current_token_payload(
    token: Optional[str] = Depends(oauth2_scheme) if settings.AUTH_ENABLED else None,
) -> Dict[str, Any]:
    if not settings.AUTH_ENABLED:
        # Auth disabled → do nothing, let everyone in
        return {}

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing token",
        )

    return decode_access_token(token)
