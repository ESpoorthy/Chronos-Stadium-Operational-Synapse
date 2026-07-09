"""
Centralised application settings using Pydantic Settings.

All configuration is read from environment variables (or a .env file).
Accessing `settings` from anywhere in the app gives a single validated
configuration object — preventing scattered os.getenv() calls.
"""
import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    """Application-wide settings derived from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Application ──────────────────────────────────────────────────────────
    app_name: str = Field(default="Chronos Stadium AI", description="Human-readable application name.")
    environment: str = Field(default="development", description="Deployment environment: development | production.")
    log_level: str = Field(default="INFO", description="Python logging level.")

    # ── Database ─────────────────────────────────────────────────────────────
    database_url: str = Field(
        default="postgresql+asyncpg://chronos:chronos_password@localhost:5432/chronos_db",
        description="Async SQLAlchemy connection string.",
    )

    # ── CORS ─────────────────────────────────────────────────────────────────
    allowed_origins: str = Field(
        default="http://localhost:3000",
        description="Comma-separated list of allowed CORS origins.",
    )

    # ── Rate Limiting ─────────────────────────────────────────────────────────
    rate_limit_per_minute: int = Field(default=100, ge=1, description="Max requests per minute per IP.")

    # ── AI / LLM ──────────────────────────────────────────────────────────────
    gemini_api_key: str = Field(default="", description="Google Gemini API key.")

    @property
    def is_production(self) -> bool:
        """Returns True when the app is running in production mode."""
        return self.environment.lower() == "production"

    @property
    def parsed_allowed_origins(self) -> list[str]:
        """Returns CORS allowed_origins as a parsed list."""
        return [o.strip() for o in self.allowed_origins.split(",") if o.strip()]


settings = Settings()
