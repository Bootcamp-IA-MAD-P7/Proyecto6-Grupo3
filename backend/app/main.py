"""FastAPI entrypoint. Run from the repository root:

    uv run uvicorn backend.app.main:app --reload --port 8000

See backend/README.md for setup and how to try the endpoints.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import load_settings
from .errors import register_error_handlers
from .routes.analyze import router as analyze_router
from .routes.health import router as health_router

settings = load_settings()

app = FastAPI(title="PrivacyLens API", version="0.1.0")

# CORS origin comes from an env var, never hardcoded and never "*"
# (specs/5_backend_contract.md, SEGURIDAD minimo 3).
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allowed_origins_list,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

register_error_handlers(app)

app.include_router(health_router, prefix="/api")
app.include_router(analyze_router, prefix="/api")
