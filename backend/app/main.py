"""
FastAPI application entry point.

Responsibilities
----------------
- Configure structured logging.
- Attach rate-limiting middleware (slowapi).
- Inject security headers on every response.
- Restrict CORS to configured origins.
- Mount application routers.

All configuration values come from ``app.config.settings`` (a Pydantic
Settings model), which reads from environment variables / ``.env`` file.
This replaces scattered ``os.getenv()`` calls with a single, validated
source of truth.
"""
import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from starlette.middleware.base import BaseHTTPMiddleware

from app.config.settings import settings
from app.routers import ai

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

# ── Rate Limiter ──────────────────────────────────────────────────────────────
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[f"{settings.rate_limit_per_minute}/minute"],
)

# ── Application ───────────────────────────────────────────────────────────────
app = FastAPI(
    title=settings.app_name,
    description="The world's first Generative Future Engine for Mega Events.",
    version="1.0.0",
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


# ── Security Headers Middleware ───────────────────────────────────────────────
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Adds essential security headers to every HTTP response.

    Headers applied:
    - ``X-Content-Type-Options``: Prevents MIME-type sniffing.
    - ``X-Frame-Options``: Blocks clickjacking via iframes.
    - ``X-XSS-Protection``: Enables legacy XSS filter in older browsers.
    - ``Referrer-Policy``: Limits referrer leakage to same-origin upgrades.
    - ``Permissions-Policy``: Restricts access to sensitive browser APIs.
    - ``Strict-Transport-Security``: Enforced only in production (HTTPS required).
    """

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        if settings.is_production:
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        return response


app.add_middleware(SecurityHeadersMiddleware)

# ── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.parsed_allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "Authorization"],
)

logger.info(
    "Starting %s (env=%s) — CORS origins: %s",
    settings.app_name,
    settings.environment,
    settings.parsed_allowed_origins,
)

# ── Routes ────────────────────────────────────────────────────────────────────
@app.get("/", summary="Root health probe")
async def root():
    """Lightweight root endpoint confirming the API is running."""
    return {"message": f"{settings.app_name} Backend is running."}


@app.get("/health", summary="Health check")
async def health_check():
    """Returns ``ok`` when the application is healthy and ready to serve traffic."""
    return {"status": "ok"}


app.include_router(ai.router)
