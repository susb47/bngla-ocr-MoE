"""Application configuration loaded from environment / .env."""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="MOEDOCS_",
        extra="ignore",
    )

    # Paths
    corpus_dir: Path = Path("./corpus")
    sources_file: Path = Path("./sources.yml")
    kb_export_dir: Path | None = None  # e.g. ../moe-bot/data/kb

    # OCR
    ocr_engine: Literal["tesseract", "surya", "paddle"] = "tesseract"
    tesseract_lang: str = "ben+eng"

    # Rendering
    view_dpi: int = 150   # for the review UI
    ocr_dpi: int = 300    # for OCR engines

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    def ensure_dirs(self) -> None:
        self.corpus_dir.mkdir(parents=True, exist_ok=True)


# Singleton used across the package
settings = Settings()
settings.ensure_dirs()
