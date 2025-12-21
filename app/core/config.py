import os
from typing import Optional

from dotenv import load_dotenv
from pydantic import BaseModel, model_validator

from app import __version__

load_dotenv(override=False)


def _str_to_bool(value: str | None, default: bool = True) -> bool:
    if value is None:
        return default
    value = value.strip().lower()
    return value in ("1", "true", "yes", "on")


def _split_csv(value: str) -> list[str]:
    return [v.strip() for v in value.split(",") if v.strip()]


class Settings(BaseModel):
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "sqlite:///./shortener.db",
    )

    BASE_URL: str = os.getenv("BASE_URL", "http://127.0.0.1:8000")
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "")

    AUTH_ENABLED: bool = _str_to_bool(os.getenv("AUTH_ENABLED", "true"), default=True)

    # TODO: Implement OAuth properly later, let's focus on token atm
    # Always defined, just may be None when auth disabled
    # OAUTH2_TOKEN_URL: Optional[str] = os.getenv(
    #     "OAUTH2_TOKEN_URL",
    #     "http://localhost:8001/auth/login",
    # )
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_ISSUER: str = os.getenv("JWT_ISSUER", "auth-service")
    JWT_AUDIENCE: list[str] = _split_csv(os.getenv("JWT_AUDIENCE", "shortener-service"))

    CORS_ORIGINS: list[str] = _split_csv(os.getenv("CORS_ORIGINS", ""))

    API_VERSION: int = int(os.getenv("API_VERSION", __version__.split(".")[0]))

    # Simple in-memory rate limiting (per IP)
    RATE_LIMIT_ENABLED: bool = _str_to_bool(os.getenv("RATE_LIMIT_ENABLED", "true"))
    RATE_LIMIT_REQUESTS: int = int(os.getenv("RATE_LIMIT_REQUESTS", "30"))
    RATE_LIMIT_WINDOW_SECONDS: int = int(os.getenv("RATE_LIMIT_WINDOW_SECONDS", "60"))

    @model_validator(mode="after")
    def _validate_auth_fields(self) -> "Settings":
        """
        Enforce that when AUTH_ENABLED is True, the JWT settings are present.
        """
        if self.AUTH_ENABLED:
            if not self.JWT_SECRET_KEY:
                raise ValueError("JWT_SECRET_KEY must be set when AUTH_ENABLED=true")
            if not self.JWT_ALGORITHM:
                raise ValueError("JWT_ALGORITHM must be set when AUTH_ENABLED=true")
            # if not self.OAUTH2_TOKEN_URL:
            #     raise ValueError("OAUTH2_TOKEN_URL must be set when AUTH_ENABLED=true")
        return self


settings = Settings()
