from typing import Generator

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db


# Use a separate SQLite DB for tests (file-based so it's shared across connections)
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_shortener.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db() -> Generator:
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


# Create tables in the test DB
Base.metadata.create_all(bind=engine)

# Override the dependency in the FastAPI app
app.dependency_overrides[get_db] = override_get_db


def get_test_client() -> TestClient:
    return TestClient(app)