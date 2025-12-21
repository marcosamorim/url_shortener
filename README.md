# URL Shortener (FastAPI + SQLAlchemy)

A lightweight and extensible URL shortener service built with **FastAPI**, **SQLAlchemy**, and **SQLite**.
This project was created primarily for learning and as a base for future microservice integrations.

---

## Related Services

These repos are related but designed to run standalone as well:

- Auth service: https://github.com/marcosamorim/auth-service
- Angular frontend: https://github.com/marcosamorim/url_shortener_ng

---

## 🚀 Features

- Shorten any valid HTTP/HTTPS URL
- Random unique 6-character codes
- Automatic redirects using **307 Temporary Redirect**
- Stores links in a SQLite database
- Tracks number of clicks
- Clean project structure using routers, models, and schemas
- Fully typed (Pydantic v2 + SQLAlchemy)
- Auto-generated interactive API docs via Swagger/OpenAPI

---

## 🧱 Project Structure

```
app/
├── api/
│   └── shortener.py       # Router (endpoints)
├── database.py            # Engine, session factory, dependency
├── main.py                # FastAPI app + router includes
├── models.py              # SQLAlchemy models
└── schemas.py             # Pydantic models (request/response)
```

---

## 🔧 Installation

Clone the repo:

```bash
git clone https://github.com/marcosamorim/url_shortener.git
cd url_shortener
```

Create a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate  # macOS/Linux
# or
# .venv\Scripts\activate   # Windows
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## ▶️ Running the Server

Start the FastAPI app with Uvicorn:

```bash
uvicorn app.main:app --reload
```

Visit:

- API Docs → http://127.0.0.1:8000/docs
- ReDoc → http://127.0.0.1:8000/redoc

---

## 🐳 Docker Compose (optional)

Run the full microservice stack locally:

```bash
docker compose up
```

To build just this service locally while the others use images, keep the same command and add a `docker-compose.override.yml` with a `build:` for this repo (already provided).

---

## 📌 Usage

### 1. Shorten a URL
**POST** `/shorten`

Example request:

```json
{
  "url": "https://www.google.com"
}
```

Example response:

```json
{
  "code": "aB3k9X",
  "short_url": "http://localhost:8000/aB3k9X",
  "original_url": "https://www.google.com"
}
```

### 2. Redirect
Open the generated short URL in the browser:

```
GET /aB3k9X
```

### 3. Stats
**GET** `/api/stats/{code}`

Returns click count and metadata.

---

## 🛠️ Tech Stack

- **FastAPI** — web framework
- **SQLAlchemy ORM** — database layer
- **SQLite** — lightweight storage
- **Pydantic v2** — data validation and serialization
- **Uvicorn** — ASGI server

---

## 🔐 Auth Integration (JWT)

This service can validate JWTs issued by the [`auth-service`](https://github.com/marcosamorim/auth-service) and uses the token to:
- tag ownership on `/api/shorten`
- gate private stats on `/api/stats/{code}`

Set these env vars to match the auth service:

```
AUTH_ENABLED=true
JWT_SECRET_KEY=change_me
JWT_ALGORITHM=HS256
JWT_ISSUER=auth-service
JWT_AUDIENCE=shortener-service
```

If you want a standalone mode without auth, set `AUTH_ENABLED=false`.

---

## 📌 API Versioning

The API is versioned under `/api/v{major}`. The major version is driven by `API_VERSION` (env var), which defaults to the major from `app.__version__`. We keep `/api` as a legacy alias while clients migrate.

---

## 🧰 Rate Limiting (simple, in-memory)

`POST /api/shorten` is protected with a lightweight in‑memory rate limiter keyed by client IP. Configure via:

```
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS=30
RATE_LIMIT_WINDOW_SECONDS=60
```

This is intended for learning/local use and can be replaced with a gateway‑level or Redis‑backed limiter later.

---

## 🧭 Design Notes

This service is live, so security is prioritized. The original idea was to keep all features open when `AUTH_ENABLED=false`, but user‑scoped endpoints (like `GET /api/me/urls`) are intentionally locked. That keeps behavior closer to a production‑grade service and avoids accidental data exposure.

---

## 📦 Future Improvements

This project is intentionally minimal, but can be easily extended:

- Async SQLAlchemy (async engine + async sessions)
- Custom aliases / slugs
- Link expiration (`expires_at`)
- User accounts + per-user stats
- Owner-only metadata surfaced in user dashboards (e.g., client_id)
- Redis caching for redirect lookup
- Docker image for deployment
- Postgres/MySQL backends
- QR code generation
- Rate limiting
- Analytics dashboard

---

## 📄 License

MIT — you’re free to use it in personal or commercial projects.

---

## 🙌 Contributing

Pull requests and improvements are welcome!
