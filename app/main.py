from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import __version__
from app.api import redirect as redirect_router
from app.api import shortener as shortener_router
from app.core.config import settings

app = FastAPI(title="URL Shortener Service", version=__version__)


if settings.CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type"],
    )


@app.get("/health")
def health():
    return {"status": "ok"}


app.include_router(shortener_router.router)
app.include_router(redirect_router.router)
