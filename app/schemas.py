from datetime import datetime
from typing import Any

from pydantic import AnyHttpUrl, BaseModel

from app.enums import SourceType


class ShortenRequest(BaseModel):
    url: AnyHttpUrl
    # optional metadata your other services can send
    extras: dict[str, Any] | None = None


class ShortenResponse(BaseModel):
    code: str
    short_url: str
    original_url: str


class PublicURLStats(BaseModel):
    code: str
    original_url: str


class PrivateURLStats(BaseModel):
    code: str
    original_url: str

    owner_client_id: str
    created_by_user_id: str | None = None

    created_at: datetime
    expires_at: datetime | None = None
    is_active: bool

    source_type: SourceType
    clicks: int
    extras: dict[str, Any] | None = None


class MyUrlItem(BaseModel):
    code: str
    short_url: str
    original_url: str
    clicks: int
    created_at: datetime


class MyUrlsResponse(BaseModel):
    items: list[MyUrlItem]
    page: int
    page_size: int
    total: int
