from typing import Any, Dict, Optional

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.config import settings

# Don't auto-error here. We'll decide per dependency.
bearer_optional = HTTPBearer(auto_error=False)
bearer_required = HTTPBearer(auto_error=True)


def decode_access_token(token: str) -> Dict[str, Any]:
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
            audience=settings.JWT_AUDIENCE,
            options={"require": ["exp", "iat", "iss", "aud", "sub"]},
        )

        # explicit issuer check (good)
        if payload.get("iss") != settings.JWT_ISSUER:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token issuer",
            )

        return payload

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidAudienceError:
        raise HTTPException(status_code=401, detail="Invalid token audience")
    except jwt.InvalidIssuerError:
        raise HTTPException(status_code=401, detail="Invalid token issuer")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


def get_optional_token_payload(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_optional),
) -> Optional[Dict[str, Any]]:
    """
    - If AUTH is disabled: always returns None (treat as anonymous).
    - If no Authorization header: returns None.
    - If Authorization present but invalid: 401.
    - If valid: returns decoded payload.
    """
    if not settings.AUTH_ENABLED:
        return None

    if credentials is None:
        return None

    return decode_access_token(credentials.credentials)


def get_required_token_payload(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_required),
) -> Dict[str, Any]:
    """
    - If AUTH is disabled: 501 (or 403). This endpoint is meaningless without auth.
    - If enabled: requires Bearer token.
    """
    if not settings.AUTH_ENABLED:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Auth is disabled for this deployment",
        )

    return decode_access_token(credentials.credentials)
