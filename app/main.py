from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from app import __version__
from app.api import redirect as redirect_router
from app.api import shortener as shortener_router
from app.api.helpers import api_version_prefix
from app.core.config import settings

app = FastAPI(title="URL Shortener Service", version=__version__)


if settings.CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET", "POST", "OPTIONS", "PATCH", "DELETE"],
        allow_headers=["Authorization", "Content-Type"],
    )


@app.get("/health", include_in_schema=False)
def health():
    return {"status": "ok"}


@app.get("/", include_in_schema=False)
def root():
    if settings.FRONTEND_URL:
        return RedirectResponse(url=settings.FRONTEND_URL, status_code=302)
    # Standalone / no frontend configured
    return {"service": "shortener", "status": "ok"}


# Legacy API kept for backward compatibility while clients migrate to /api/v{major}.
app.include_router(shortener_router.router, prefix="/api")
app.include_router(shortener_router.router, prefix=api_version_prefix())
app.include_router(redirect_router.router)
