import os
from typing import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app

TEST_DB_PATH = "./test_shortener.db"
SQLALCHEMY_DATABASE_URL = f"sqlite:///{TEST_DB_PATH}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False)


@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """Create the test DB once at test session startup, and delete it after."""
    # Create tables for the test DB
    Base.metadata.create_all(bind=engine)

    yield  # Run the actual tests here

    # Cleanup after all tests finish
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)


# Override the DB dependency
def override_get_db() -> Generator:
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture()
def db_session():
    """Provide a DB session for direct test setup/inspection."""
    connection = engine.connect()
    transaction = connection.begin()
    db = TestingSessionLocal(bind=connection)

    db.begin_nested()

    @event.listens_for(db, "after_transaction_end")
    def restart_savepoint(session, trans):
        if trans.nested and not trans._parent.nested:
            session.begin_nested()

    try:
        yield db
    finally:
        db.close()
        transaction.rollback()
        connection.close()


@pytest.fixture()
def client(db_session) -> TestClient:
    """Provide a fresh TestClient for each test with transactional DB."""

    def override_get_db() -> Generator:
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    test_client = TestClient(app)
    yield test_client
    app.dependency_overrides.clear()
