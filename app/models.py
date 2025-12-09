from sqlalchemy import JSON, Boolean, Column, DateTime, Enum, Integer, String, func

from app.database import Base
from app.enums import SourceType


class ShortUrl(Base):
    __tablename__ = "short_urls"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(16), unique=True, index=True, nullable=False)
    original_url = Column(String(2048), index=True, nullable=False)

    # Which app/service created this link
    owner_client_id = Column(String(64), index=True, nullable=False, default="default")
    # Which user created it (from your auth system), optional for now
    created_by_user_id = Column(String(128), index=True, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=True)
    # in case we want to disable the link for any reason
    is_active = Column(Boolean, default=True, nullable=False)

    source_type = Column(
        Enum(SourceType, name="source_type_enum"),
        nullable=False,
        default=SourceType.ANONYMOUS,
        server_default=SourceType.ANONYMOUS.value,
    )

    # metadata
    clicks = Column(Integer, default=0, nullable=False)
    extras = Column(JSON, nullable=True)  # JSON (tags, campaign, etc.)
