# URL Shortener (FastAPI + SQLAlchemy)

A lightweight and extensible URL shortener service built with **FastAPI**, **SQLAlchemy**, and **SQLite**.  
This project was created primarily for learning and as a base for future microservice integrations.

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

## 📦 Future Improvements

This project is intentionally minimal, but can be easily extended:

- Async SQLAlchemy (async engine + async sessions)  
- Custom URL codes  
- Link expiration (`expires_at`)  
- User accounts + per-user stats  
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
