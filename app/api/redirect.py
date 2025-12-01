from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import ShortUrl
from app.schemas import ShortenRequest, ShortenResponse, ShortUrlStats

router = APIRouter(tags=["Redirect"])


@router.get("/{code}", name="redirect_to_url")
def redirect_to_url(code: str, db: Session = Depends(get_db)):
    try:
        # old style query
        # short = db.query(ShortUrl).filter_by(code=code).one()
        # new style from SQLAlchemy 2.0+
        stmt = select(ShortUrl).where(ShortUrl.code == code)
        short = db.execute(stmt).scalars().one()
    except NoResultFound:
        raise HTTPException(status_code=404, detail="Short URL not found")

    if not short.is_active:
        raise HTTPException(status_code=410, detail="Short URL inactive")

    if short.expires_at is not None:
        now = datetime.now(timezone.utc)

        if short.expires_at <= now:
            raise HTTPException(status_code=410, detail="Short URL has expired")

    short.clicks += 1
    db.commit()

    # 307 keeps method (GET stays GET, POST stays POST if ever needed)
    return RedirectResponse(url=str(short.original_url), status_code=307)
