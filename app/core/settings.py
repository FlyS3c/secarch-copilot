"""Centralized, validated application configuration."""

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Load application settings from environment variables and .env."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    secarch_data_root: Path

    ollama_host: str = "http://127.0.0.1:11434"
    generation_model: str = "llama3.2:3b"
    embedding_model: str = "embeddinggemma"

    secarch_tenant: str = "portfolio-demo"
    secarch_role: str = "security-architect"
    secarch_clearance_rank: int = Field(default=1, ge=0, le=1)
    secarch_local_api_key: str = Field(min_length=24)

    secarch_active_collection: str = Field(min_length=1)
    secarch_max_distance: float = Field(gt=0)

    max_input_chars: int = Field(default=12000, ge=100, le=50000)
    max_results: int = Field(default=4, ge=1, le=8)
    request_timeout_seconds: int = Field(
        default=180,
        ge=5,
        le=180,
    )

    max_request_body_bytes: int = Field(
        default=65_536,
        ge=1_024,
        le=1_048_576,
    )
    rate_limit_requests: int = Field(
        default=12,
        ge=1,
        le=100,
    )
    rate_limit_window_seconds: int = Field(
        default=60,
        ge=1,
        le=3_600,
    )

    max_output_tokens: int = Field(
        default=2_048,
        ge=128,
        le=4_096,
    )
    max_concurrent_model_requests: int = Field(
        default=1,
        ge=1,
        le=2,
    )

    @property
    def chroma_path(self) -> Path:
        """Return the Chroma directory located outside the repository."""

        return self.secarch_data_root / "chroma"

    @property
    def audit_log_path(self) -> Path:
        """Return the audit-log file outside the repository."""

        return (
            self.secarch_data_root
            / "logs"
            / "secarch-audit.jsonl"
        )


settings = Settings()