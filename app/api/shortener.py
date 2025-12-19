from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.helpers import generate_code
from app.core.config import settings
from app.database import get_db
from app.enums import SourceType
from app.models import ShortUrl
from app.rate_limit import enforce_rate_limit
from app.schemas import MyUrlItem, MyUrlsResponse, ShortenRequest, ShortenResponse
from app.security import get_optional_token_payload, get_required_token_payload

router = APIRouter(prefix="/api", tags=["shortener"])


@router.post("/shorten", response_model=ShortenResponse)
def create_short_url(
    data: ShortenRequest,
    request: Request,
    db: Session = Depends(get_db),
    token_payload: dict = Depends(get_optional_token_payload),
):
    """
    Always creates a NEW short URL.

    Ownership:
      - created_by_user_id = JWT 'sub' when auth enabled, else None
      - owner_client_id    = JWT 'client_id' when present, else 'unknown' / 'anonymous'
      - source_type        = 'human' | 'service' | 'anonymous'
    """
    url_str = str(data.url)

    forwarded_for = request.headers.get("x-forwarded-for")
    client_ip = (
        forwarded_for.split(",")[0].strip()
        if forwarded_for
        else (request.client.host if request.client else "unknown")
    )
    enforce_rate_limit(f"{client_ip}:shorten")

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
    token_payload: Optional[dict[str, Any]] = Depends(get_optional_token_payload),
):
    """
    Stats visibility rules:
    - Anonymous: clicks only
    - Authenticated owner: full stats
    - Authenticated non-owner: public stats
    """
    stmt = select(ShortUrl).where(ShortUrl.code == code)
    short = db.execute(stmt).scalars().first()

    if not short:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Short URL not found",
        )

    # AUTH DISABLED → full access (standalone mode)
    if not settings.AUTH_ENABLED:
        return _private_stats_payload(short)

    # AUTH ENABLED → public vs private split
    # (if token_payload is None, that is anonymous and, we show only public stats)
    if token_payload is None:
        return _public_stats_payload(short)

    user_id = token_payload.get("sub")

    if short.created_by_user_id:
        # user-owned link → only owner sees private stats
        if str(user_id) != str(short.created_by_user_id):
            return _public_stats_payload(short)
        return _private_stats_payload(short)

    # anonymous / service-created links
    return _public_stats_payload(short)


@router.get("/me/urls", response_model=MyUrlsResponse)
def list_my_urls(
    page: int = 1,
    page_size: int = 10,
    db: Session = Depends(get_db),
    token_payload: dict = Depends(get_required_token_payload),
):
    """
    List URLs created by the authenticated user.
    """
    if page < 1 or page_size < 1 or page_size > 50:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid pagination params",
        )

    user_id = token_payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload (missing sub)",
        )

    stmt = select(ShortUrl).where(ShortUrl.created_by_user_id == str(user_id))
    total = db.execute(select(func.count()).select_from(stmt.subquery())).scalar_one()

    urls = (
        db.execute(
            stmt.order_by(ShortUrl.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        .scalars()
        .all()
    )

    items = [
        MyUrlItem(
            code=short.code,
            short_url=f"{settings.BASE_URL}/{short.code}",
            original_url=short.original_url,
            clicks=short.clicks,
            created_at=short.created_at,
        )
        for short in urls
    ]

    return MyUrlsResponse(items=items, page=page, page_size=page_size, total=total)


def _public_stats_payload(short: ShortUrl) -> dict[str, Any]:
    return {
        "code": short.code,
        "original_url": short.original_url,
        "created_at": short.created_at,
    }


def _private_stats_payload(short: ShortUrl) -> dict[str, Any]:
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
