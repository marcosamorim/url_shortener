import secrets
import string

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import ShortUrl
from app.schemas import ShortenRequest, ShortenResponse, ShortUrlStats

router = APIRouter(prefix="/api", tags=["API"])


def generate_code(db: Session, length: int = 6) -> str:
    alphabet = string.ascii_letters + string.digits
    while True:
        code = "".join(secrets.choice(alphabet) for _ in range(length))
        if not db.query(ShortUrl).filter_by(code=code).first():
            return code


@router.post("/shorten", response_model=ShortenResponse)
def create_short_url(
    data: ShortenRequest, request: Request, db: Session = Depends(get_db)
):

    url_str = str(data.url)

    # generate the code for the new short url
    code = generate_code(db)
    # save the short url to the database
    # TODO: resolve real client_id and user_id from headers/JWT
    short = ShortUrl(
        code=code,
        original_url=url_str,
        # TODO: add client_id and user_id from headers/JWT
        # owner_client_id="default",
        # created_by_user_id=None,
        # TODO: insert expires_at logic here in future
        # expires_at left as None for now – can add API control later
        extras=data.extras,
    )
    db.add(short)
    db.commit()
    # refresh the short url to get the id
    db.refresh(short)

    short_url = str(request.url_for("redirect_to_url", code=short.code))

    return ShortenResponse(
        code=short.code,
        short_url=short_url,
        original_url=url_str,
    )


@router.get("/stats/{code}", response_model=ShortUrlStats)
def get_stats(code: str, db: Session = Depends(get_db)):
    try:
        stmt = select(ShortUrl).where(ShortUrl.code == code)
        short = db.execute(stmt).scalars().one()
    except NoResultFound:
        raise HTTPException(status_code=404, detail="Short URL not found")

    return ShortUrlStats(
        code=short.code,
        original_url=short.original_url,
        owner_client_id=short.owner_client_id,
        created_by_user_id=short.created_by_user_id,
        created_at=short.created_at,
        expires_at=short.expires_at,
        is_active=short.is_active,
        clicks=short.clicks,
        extras=short.extras,
    )
