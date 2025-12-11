import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel

from app.core.config import settings


def _get_database_url() -> str:
    """
    Resolve the DB URL:

    - Normalize postgres:// → postgresql+psycopg:// for SQLAlchemy.
    """
    db_url = os.getenv("DATABASE_URL", settings.DATABASE_URL)

    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql+psycopg://", 1)
    elif db_url.startswith("postgresql://") and "+psycopg" not in db_url:
        db_url = db_url.replace("postgresql://", "postgresql+psycopg://", 1)

    return db_url


SQLALCHEMY_DATABASE_URI = _get_database_url()

connect_args: dict = {}
if SQLALCHEMY_DATABASE_URI.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    SQLALCHEMY_DATABASE_URI,
    connect_args=connect_args,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


Base = SQLModel


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
