# app/main.py
from fastapi import FastAPI

from app.database import Base, engine
from app.api import shortener as shortener_router

# Create tables on startup (simple way for a small project)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="URL Shortener Service")


@app.get("/health")
def health():
    return {"status": "ok"}


app.include_router(shortener_router.router)