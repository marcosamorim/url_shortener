import secrets
import string
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import ShortUrl

CODE_LENGTH = 6
CODE_ALPHABET = string.ascii_letters + string.digits


def generate_code(db: Session) -> str:
    """
    Generate a unique short code.
    Uses a simple random approach with collision check.
    For very high volume you'd want something more robust.
    """
    while True:
        code = "".join(secrets.choice(CODE_ALPHABET) for _ in range(CODE_LENGTH))

        stmt = select(ShortUrl).where(ShortUrl.code == code)
        exists = db.execute(stmt).scalars().first()
        if not exists:
            return code


def is_expired(short: ShortUrl) -> bool:
    if short.expires_at is None:
        return False
    # Convert now to timezone-aware
    now = datetime.now(timezone.utc)
    expires_at = short.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    return expires_at <= now


def api_version_prefix() -> str:
    from app.core.config import settings

    return f"/api/v{settings.API_VERSION}"
