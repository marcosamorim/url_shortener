from datetime import datetime
from typing import Any

from pydantic import AnyHttpUrl, BaseModel

from app.enums import SourceType


class ShortenRequest(BaseModel):
    url: AnyHttpUrl
    # optional metadata your other services can send
    expires_at: datetime | None = None
    extras: dict[str, Any] | None = None


class ShortenResponse(BaseModel):
    code: str
    short_url: str
    original_url: str


class PublicURLStats(BaseModel):
    code: str
    original_url: str
    created_at: datetime


class PrivateURLStats(BaseModel):
    code: str
    original_url: str

    owner_client_id: str
    created_by_user_id: str | None = None

    created_at: datetime
    is_active: bool
    expires_at: datetime | None = None

    source_type: SourceType
    clicks: int
    extras: dict[str, Any] | None = None


class LinkUpdateRequest(BaseModel):
    is_active: bool | None = None
    expires_at: datetime | None = None


class MyUrlItem(BaseModel):
    code: str
    short_url: str
    original_url: str
    clicks: int
    created_at: datetime
    is_active: bool
    expires_at: datetime | None = None


class MyUrlsResponse(BaseModel):
    items: list[MyUrlItem]
    page: int
    page_size: int
    total: int
