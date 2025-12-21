from datetime import datetime, timedelta, timezone

import jwt
import pytest
from fastapi.testclient import TestClient

from app.api.helpers import api_version_prefix
from app.core.config import settings
from tests.conftest import client


@pytest.fixture()
def restore_auth_settings():
    original = {
        "AUTH_ENABLED": settings.AUTH_ENABLED,
        "JWT_SECRET_KEY": settings.JWT_SECRET_KEY,
        "JWT_ALGORITHM": settings.JWT_ALGORITHM,
        "JWT_ISSUER": settings.JWT_ISSUER,
        "JWT_AUDIENCE": list(settings.JWT_AUDIENCE),
    }
    yield
    settings.AUTH_ENABLED = original["AUTH_ENABLED"]
    settings.JWT_SECRET_KEY = original["JWT_SECRET_KEY"]
    settings.JWT_ALGORITHM = original["JWT_ALGORITHM"]
    settings.JWT_ISSUER = original["JWT_ISSUER"]
    settings.JWT_AUDIENCE = original["JWT_AUDIENCE"]


def _set_auth(enabled: bool):
    settings.AUTH_ENABLED = enabled
    if enabled:
        settings.JWT_SECRET_KEY = "test-secret"
        settings.JWT_ALGORITHM = "HS256"
        settings.JWT_ISSUER = "auth-service"
        settings.JWT_AUDIENCE = ["shortener-service"]


def _make_token(sub: str = "user-123", client_id: str = "angular-web") -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": sub,
        "client_id": client_id,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=30)).timestamp()),
        "iss": settings.JWT_ISSUER,
        "aud": "shortener-service",
    }
    return jwt.encode(
        payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )


def test_stats_public_when_auth_enabled(client: TestClient, restore_auth_settings):
    _set_auth(True)

    resp = client.post(
        f"{api_version_prefix()}/shorten", json={"url": "https://example.com"}
    )
    assert resp.status_code == 200
    code = resp.json()["code"]

    stats_resp = client.get(f"{api_version_prefix()}/stats/{code}")
    assert stats_resp.status_code == 200
    stats = stats_resp.json()
    assert stats["code"] == code
    assert stats["original_url"].rstrip("/") == "https://example.com"
    assert "clicks" not in stats


def test_stats_private_when_auth_disabled(client: TestClient, restore_auth_settings):
    _set_auth(False)

    resp = client.post(
        f"{api_version_prefix()}/shorten", json={"url": "https://example.com"}
    )
    assert resp.status_code == 200
    code = resp.json()["code"]

    stats_resp = client.get(f"{api_version_prefix()}/stats/{code}")
    assert stats_resp.status_code == 200
    stats = stats_resp.json()
    assert stats["code"] == code
    assert stats["original_url"].rstrip("/") == "https://example.com"
    assert stats["is_active"] is True


def test_me_urls_requires_auth_when_enabled(client: TestClient, restore_auth_settings):
    _set_auth(True)

    resp = client.get(f"{api_version_prefix()}/me/urls")
    assert resp.status_code == 403


def test_me_urls_returns_403_when_auth_disabled(
    client: TestClient, restore_auth_settings
):
    _set_auth(False)

    resp = client.get(f"{api_version_prefix()}/me/urls")
    assert resp.status_code == 403


def test_me_urls_rejects_invalid_token(client: TestClient, restore_auth_settings):
    _set_auth(True)

    resp = client.get(
        f"{api_version_prefix()}/me/urls", headers={"Authorization": "Bearer bad-token"}
    )
    assert resp.status_code == 401


def test_me_urls_returns_owned_links(client: TestClient, restore_auth_settings):
    _set_auth(True)

    token = _make_token(sub="user-123")
    headers = {"Authorization": f"Bearer {token}"}

    create_resp = client.post(
        f"{api_version_prefix()}/shorten",
        json={"url": "https://example.com/my-link"},
        headers=headers,
    )
    assert create_resp.status_code == 200
    code = create_resp.json()["code"]

    list_resp = client.get(
        f"{api_version_prefix()}/me/urls?page=1&page_size=10",
        headers=headers,
    )
    assert list_resp.status_code == 200
    data = list_resp.json()
    assert data["page"] == 1
    assert data["page_size"] == 10
    assert data["total"] >= 1

    codes = {item["code"] for item in data["items"]}
    assert code in codes


def test_me_urls_rejects_invalid_pagination(client: TestClient, restore_auth_settings):
    _set_auth(True)

    token = _make_token(sub="user-123")
    headers = {"Authorization": f"Bearer {token}"}

    resp = client.get(
        f"{api_version_prefix()}/me/urls?page=0&page_size=10", headers=headers
    )
    assert resp.status_code == 400

    resp = client.get(
        f"{api_version_prefix()}/me/urls?page=1&page_size=0", headers=headers
    )
    assert resp.status_code == 400

    resp = client.get(
        f"{api_version_prefix()}/me/urls?page=1&page_size=51", headers=headers
    )
    assert resp.status_code == 400


def test_update_link_requires_owner(client: TestClient, restore_auth_settings):
    _set_auth(True)

    owner_token = _make_token(sub="owner-1")
    other_token = _make_token(sub="owner-2")

    create_resp = client.post(
        f"{api_version_prefix()}/shorten",
        json={"url": "https://example.com/owned"},
        headers={"Authorization": f"Bearer {owner_token}"},
    )
    assert create_resp.status_code == 200
    code = create_resp.json()["code"]

    update_resp = client.patch(
        f"{api_version_prefix()}/links/{code}",
        json={"is_active": False},
        headers={"Authorization": f"Bearer {other_token}"},
    )
    assert update_resp.status_code == 403


def test_update_link_allows_owner_and_updates(
    client: TestClient, restore_auth_settings
):
    _set_auth(True)

    owner_token = _make_token(sub="owner-1")
    headers = {"Authorization": f"Bearer {owner_token}"}

    create_resp = client.post(
        f"{api_version_prefix()}/shorten",
        json={"url": "https://example.com/owned-update"},
        headers=headers,
    )
    assert create_resp.status_code == 200
    code = create_resp.json()["code"]

    update_resp = client.patch(
        f"{api_version_prefix()}/links/{code}",
        json={"is_active": False},
        headers=headers,
    )
    assert update_resp.status_code == 200
    data = update_resp.json()
    assert data["code"] == code
    assert data["is_active"] is False


def test_delete_link_soft_deletes(client: TestClient, restore_auth_settings):
    _set_auth(True)

    owner_token = _make_token(sub="owner-1")
    headers = {"Authorization": f"Bearer {owner_token}"}

    create_resp = client.post(
        f"{api_version_prefix()}/shorten",
        json={"url": "https://example.com/owned-delete"},
        headers=headers,
    )
    assert create_resp.status_code == 200
    code = create_resp.json()["code"]

    delete_resp = client.delete(
        f"{api_version_prefix()}/links/{code}",
        headers=headers,
    )
    assert delete_resp.status_code == 204

    stats_resp = client.get(f"{api_version_prefix()}/stats/{code}", headers=headers)
    assert stats_resp.status_code == 404
