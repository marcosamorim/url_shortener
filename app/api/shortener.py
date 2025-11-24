import string
import secrets

from fastapi import HTTPException, Depends, APIRouter, Request
from fastapi.responses import RedirectResponse

from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import ShortUrl
from app.schemas import ShortenResponse, ShortUrlStats, ShortenRequest

router = APIRouter(tags=["shortener"])


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
    # TODO: insert expires_at logic here in future
    # save the short url to the database
    short = ShortUrl(code=code, original_url=url_str)
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


@router.get("/{code}", name="redirect_to_url")
def redirect_to_url(code: str, db: Session = Depends(get_db)):
    try:
        short = db.query(ShortUrl).filter_by(code=code).one()
    except NoResultFound:
        raise HTTPException(status_code=404, detail="Short URL not found")

    # if not short:
    #     raise HTTPException(status_code=404, detail="Short URL not found")

    if not short.is_active:
        raise HTTPException(status_code=410, detail="Short URL inactive")

    short.clicks += 1
    db.commit()

    # 307 keeps method (GET stays GET, POST stays POST if ever needed)
    return RedirectResponse(url=str(short.original_url), status_code=307)


@router.get("/api/stats/{code}", response_model=ShortUrlStats)
def get_stats(code: str, db: Session = Depends(get_db)):
    try:
        short = db.query(ShortUrl).filter_by(code=code).one()
    except NoResultFound:
        raise HTTPException(status_code=404, detail="Short URL not found")

    return ShortUrlStats(
        code=short.code,
        original_url=short.original_url,
        clicks=short.clicks,
    )
