"""Tests for centralized application settings."""

from pathlib import Path

import pytest
from pydantic import ValidationError

from app.core.settings import Settings


def valid_settings(tmp_path: Path, **overrides) -> Settings:
    """Create isolated settings without reading the repository .env file."""

    values = {
        "secarch_data_root": tmp_path,
        "secarch_local_api_key": "test-only-key-with-at-least-24-characters",
        "secarch_active_collection": "secarch_knowledge_test_v1",
        "secarch_max_distance": 1.207854,
    }

    values.update(overrides)

    return Settings(
        _env_file=None,
        **values,
    )


def test_valid_settings_are_loaded(tmp_path: Path) -> None:
    application_settings = valid_settings(tmp_path)

    assert application_settings.generation_model == "llama3.2:3b"
    assert application_settings.embedding_model == "embeddinggemma"
    assert application_settings.secarch_tenant == "portfolio-demo"
    assert application_settings.max_results == 4
    assert application_settings.chroma_path == tmp_path / "chroma"


def test_short_api_key_is_rejected(tmp_path: Path) -> None:
    with pytest.raises(ValidationError):
        valid_settings(
            tmp_path,
            secarch_local_api_key="too-short",
        )


def test_invalid_clearance_is_rejected(tmp_path: Path) -> None:
    with pytest.raises(ValidationError):
        valid_settings(
            tmp_path,
            secarch_clearance_rank=2,
        )


def test_invalid_result_limit_is_rejected(tmp_path: Path) -> None:
    with pytest.raises(ValidationError):
        valid_settings(
            tmp_path,
            max_results=9,
        )


def test_invalid_distance_threshold_is_rejected(
    tmp_path: Path,
) -> None:
    with pytest.raises(ValidationError):
        valid_settings(
            tmp_path,
            secarch_max_distance=0,
        )