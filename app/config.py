"""Runtime configuration loaded from .env."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    redis_url: str = Field(default="redis://localhost:6379/0")
    redis_key_prefix: str = Field(default="page-to-md")

    mail_host: str = Field(default="smtp.gmail.com")
    mail_port: int = Field(default=587)
    mail_user: str = Field(default="")
    mail_password: str = Field(default="")
    mail_from_name: str = Field(default="Page to Markdown")
    mail_from_address: str = Field(default="noreply@example.com")
    mail_starttls: bool = Field(default=True)

    public_base_url: str = Field(default="http://localhost:8000")

    job_ttl_seconds: int = Field(default=3600)
    job_dir: Path = Field(default=Path("/tmp/page-to-md-jobs"))


@lru_cache
def get_settings() -> Settings:
    return Settings()
