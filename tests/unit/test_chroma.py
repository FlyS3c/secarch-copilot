"""Tests for security-focused Chroma configuration."""

from app.core.chroma import build_chroma_settings


def test_chroma_product_telemetry_is_disabled() -> None:
    configuration = build_chroma_settings()

    assert configuration.anonymized_telemetry is False
