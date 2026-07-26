"""Backend configuration, read from environment variables — never hardcoded
(see specs/5_backend_contract.md, REGLAS DURAS)."""

from pathlib import Path

from pydantic import ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parent.parent

# Fixed by specs/5_backend_contract.md (SEGURIDAD, minimo 2). Not env-configurable:
# it is a security floor, not a deployment knob.
MAX_TEXT_LENGTH = 100_000


class Settings(BaseSettings):
    cors_allowed_origins: str

    model_config = SettingsConfigDict(
        env_file=BACKEND_DIR / ".env",
        env_file_encoding="utf-8",
    )

    @property
    def cors_allowed_origins_list(self) -> list[str]:
        return [
            origin.strip()
            for origin in self.cors_allowed_origins.split(",")
            if origin.strip()
        ]


def load_settings() -> Settings:
    try:
        return Settings()
    except ValidationError as exc:
        raise RuntimeError(
            "Missing backend configuration: CORS_ALLOWED_ORIGINS is not set. "
            "Copy backend/.env.example to backend/.env and set it there."
        ) from exc
