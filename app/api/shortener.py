from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.helpers import generate_code
from app.core.config import settings
from app.database import get_db
from app.enums import SourceType
from app.models import ShortUrl
from app.schemas import ShortenRequest, ShortenResponse
from app.security import get_current_token_payload

router = APIRouter(prefix="/api", tags=["shortener"])


@router.post("/shorten", response_model=ShortenResponse)
def create_short_url(
    data: ShortenRequest,
    db: Session = Depends(get_db),
    token_payload: dict = Depends(get_current_token_payload),
):
    """
    Always creates a NEW short URL.

    Ownership:
      - created_by_user_id = JWT 'sub' when auth enabled, else None
      - owner_client_id    = JWT 'client_id' when present, else 'unknown' / 'anonymous'
      - source_type        = 'human' | 'service' | 'anonymous'
    """
    url_str = str(data.url)

    user_id = token_payload.get("sub") if token_payload else None
    client_id = token_payload.get("client_id") if token_payload else None

    if token_payload:
        if user_id:
            source_type = SourceType.HUMAN
        else:
            source_type = SourceType.SERVICE
    else:
        source_type = SourceType.ANONYMOUS

    code = generate_code(db)

    owner_client_id = client_id or (
        SourceType.ANONYMOUS if not token_payload else SourceType.UNKNOWN
    )

    short = ShortUrl(
        code=code,
        original_url=url_str,
        owner_client_id=owner_client_id,
        created_by_user_id=user_id,
        source_type=source_type,
        extras=data.extras,
    )

    db.add(short)
    db.commit()
    db.refresh(short)

    return ShortenResponse(
        code=short.code,
        short_url=f"{settings.BASE_URL}/{short.code}",
        original_url=short.original_url,
    )


@router.get("/stats/{code}")
def get_stats(
    code: str,
    db: Session = Depends(get_db),
    token_payload: dict = Depends(get_current_token_payload),
):
    stmt = select(ShortUrl).where(ShortUrl.code == code)
    short = db.execute(stmt).scalars().first()

    if not short:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Short URL not found",
        )

    # AUTH_DISABLED → stats public
    if not settings.AUTH_ENABLED:
        return _stats_payload(short)

    # AUTH_ENABLED → enforce user-centric rules
    user_id = token_payload.get("sub") if token_payload else None

    if short.created_by_user_id is not None:
        # user-owned link → only that user can see stats
        if user_id != short.created_by_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to view stats for this short URL",
            )
    else:
        # no user bound (service / anonymous)
        # For now: require *some* authenticated user, but don't tie to a specific sub.
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required to view stats",
            )

    return _stats_payload(short)


def _stats_payload(short: ShortUrl):
    return {
        "code": short.code,
        "original_url": short.original_url,
        "clicks": short.clicks,
        "owner_client_id": short.owner_client_id,
        "created_by_user_id": short.created_by_user_id,
        "source_type": short.source_type,
        "created_at": short.created_at,
        "expires_at": short.expires_at,
        "is_active": short.is_active,
        "extras": short.extras,
    }
