from datetime import datetime
from typing import Any, Dict, Optional

from sqlalchemy import JSON, Column, DateTime, func
from sqlmodel import Field, SQLModel

from app.enums import SourceType


class ShortUrl(SQLModel, table=True):
    __tablename__ = "shortener__short_urls"

    id: Optional[int] = Field(default=None, primary_key=True)

    code: str = Field(index=True, nullable=False, max_length=16, unique=True)
    original_url: str = Field(nullable=False, max_length=2048, index=True)

    # Which app/service created this link
    owner_client_id: str = Field(
        default="default",
        nullable=False,
        max_length=64,
        index=True,
    )

    # Which user created it (from your auth system), optional
    created_by_user_id: Optional[str] = Field(
        default=None,
        max_length=128,
        index=True,
    )

    # timestamps
    created_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),
            server_default=func.now(),
            nullable=False,
        )
    )
    expires_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True),
    )

    # flags
    is_active: bool = Field(default=True, nullable=False)

    # stored as TEXT in the DB, validated as Enum in Python/Pydantic
    source_type: SourceType = Field(
        default=SourceType.ANONYMOUS,
        nullable=False,
    )

    # metadata
    clicks: int = Field(default=0, nullable=False)
    extras: Optional[Dict[str, Any]] = Field(
        default=None,
        sa_column=Column(JSON, nullable=True),
    )
