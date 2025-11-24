from sqlalchemy import Column, Integer, String, DateTime, func, Boolean, JSON

from app.database import Base


class ShortUrl(Base):
    __tablename__ = "short_urls"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(16), unique=True, index=True, nullable=False)
    original_url = Column(String(2048), index=True, nullable=False)

    # TODO: when we add auth/users later
    # created_by = Column(Integer, index=True, nullable=True) # user_id / client_id
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=True)
    # in case we want to disable the link for any reason
    is_active = Column(Boolean, default=True, nullable=False)

    # user metadata
    clicks = Column(Integer, default=0, nullable=False)
    extras = Column(JSON, nullable=True)  # JSON (tags, campaign, etc.)
