from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.database import get_db
from app.models import ShortUrl
from app.schemas import ShortenRequest, ShortenResponse
from app.security import get_current_token_payload

router = APIRouter(prefix="/", tags=["redirect"])

# ---------------------------
# Public redirect endpoint
# ---------------------------


@public_router.get("/{code}", name="redirect_to_url")
def redirect_to_url(code: str, db: Session = Depends(get_db)):
    """
    Public redirect:
      - No auth ever required
      - Checks is_active and expires_at
      - Increments click count
    """
    stmt = select(ShortUrl).where(ShortUrl.code == code)
    short = db.execute(stmt).scalars().first()

    if not short or not short.is_active or is_expired(short):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Short URL not found or inactive",
        )

    # Increment clicks
    short.clicks += 1
    db.add(short)
    db.commit()

    return RedirectResponse(
        url=short.original_url, status_code=status.HTTP_307_TEMPORARY_REDIRECT
    )
