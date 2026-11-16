"""
Application settings.

All environment variables are loaded once, at import time, through
pydantic-settings. Values come from (in order of increasing precedence):

  1. the project-root .env
  2. backend/.env
  3. real environment variables

Access everywhere via `from core.config import settings`.
"""

from functools import lru_cache
from pathlib import Path
from typing import List, Optional

from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = BACKEND_DIR.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        # later files take priority: backend/.env overrides the root .env
        env_file=(PROJECT_ROOT / ".env", BACKEND_DIR / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Service metadata
    app_name: str = "Trust Backend"
    app_version: str = "0.2.0"
    app_description: str = "Fact-checker API gateway over Unity Catalog + Gemini"

    # Databricks / Unity Catalog
    databricks_server_hostname: Optional[str] = None
    databricks_http_path: Optional[str] = None
    databricks_token: Optional[str] = None
    databricks_catalog: str = "workspace"
    databricks_schema: str = "trust_dev"
    # Gold stories table name — the pipeline versions this (story_records_v2)
    databricks_stories_table: str = "story_records_v2"

    # Gemini
    gemini_api_key: Optional[str] = None
    # 20s per model: with 4 fallback models the whole chain stays
    # under ~80s, inside the frontend's 120s request budget.
    gemini_timeout_ms: int = 20_000

    # CORS (comma-separated in env, e.g. CORS_ORIGINS=http://localhost:3000)
    cors_origins: str = "*"

    @property
    def cors_origin_list(self) -> List[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def table_prefix(self) -> str:
        """Fully qualified `catalog.schema` prefix for Unity Catalog tables."""
        return f"{self.databricks_catalog}.{self.databricks_schema}"

    @property
    def stories_table(self) -> str:
        """Fully qualified gold stories table."""
        return f"{self.table_prefix}.{self.databricks_stories_table}"

    @property
    def databricks_configured(self) -> bool:
        return bool(
            self.databricks_server_hostname
            and self.databricks_http_path
            and self.databricks_token
        )

    @property
    def gemini_configured(self) -> bool:
        return bool(self.gemini_api_key)


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
