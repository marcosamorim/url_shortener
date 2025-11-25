from fastapi.testclient import TestClient

from tests.conftest import client


def test_shorten_creates_short_url_and_redirect_works(client):
    # 1) Shorten a valid URL
    resp = client.post("/shorten", json={"url": "https://www.google.com"})
    assert resp.status_code == 200

    data = resp.json()
    assert "code" in data
    assert "short_url" in data
    assert data["original_url"].rstrip("/") == "https://www.google.com"

    code = data["code"]

    # 2) Hit the short URL and expect a 307 redirect
    redirect_resp = client.get(f"/{code}", follow_redirects=False)
    assert redirect_resp.status_code == 307
    assert redirect_resp.headers["location"].rstrip("/") == "https://www.google.com"


def test_shorten_rejects_invalid_url(client):
    resp = client.post("/shorten", json={"url": "not-a-url"})
    # Pydantic validation should fail and FastAPI will return 422
    assert resp.status_code == 422


def test_stats_returns_metadata_and_clicks_increment(client):
    # 1) Create a short URL
    resp = client.post("/shorten", json={"url": "https://example.com"})
    assert resp.status_code == 200
    data = resp.json()
    code = data["code"]

    # 2) Initially, zero clicks
    stats_resp = client.get(f"/api/stats/{code}")
    assert stats_resp.status_code == 200
    stats = stats_resp.json()
    assert stats["code"] == code
    assert stats["original_url"].rstrip("/") == "https://example.com"
    assert stats["clicks"] == 0
    assert stats["is_active"] is True

    # 3) Trigger a redirect once
    redirect_resp = client.get(f"/{code}", follow_redirects=False)
    assert redirect_resp.status_code == 307

    # 4) Stats should show 1 click now
    stats_resp2 = client.get(f"/api/stats/{code}")
    assert stats_resp2.status_code == 200
    stats2 = stats_resp2.json()
    assert stats2["clicks"] == 1


def test_redirect_not_found(client):
    resp = client.get("/nonexistentcode", follow_redirects=False)
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Short URL not found"
