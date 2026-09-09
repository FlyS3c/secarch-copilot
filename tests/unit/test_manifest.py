from __future__ import annotations

from copy import deepcopy
from pathlib import Path

import pytest
import yaml
from pydantic import ValidationError

from app.ingestion.manifest import load_manifest


def valid_source() -> dict:
    return {
        "source_id": "example-source",
        "title": "Example Source",
        "publisher": "Example Publisher",
        "version": "1.0",
        "official_url": "https://example.com/source",
        "retrieval_url": "https://example.com/source.txt",
        "license_name": "Example licence",
        "license_url": "https://example.com/licence",
        "retrieved_at": "2026-09-08",
        "local_relative_path": "raw/example/source.txt",
        "file_type": "txt",
        "sha256": "a" * 64,
        "tenant": "portfolio-demo",
        "allowed_roles": ["security-architect", "security-engineer"],
        "classification": "public",
        "approved": True,
        "approved_by": "Glenn Merritt",
        "approved_at": "2026-09-08",
        "notes": "Synthetic test record.",
    }


def write_manifest(path: Path, source: dict) -> Path:
    path.write_text(yaml.safe_dump({"sources": [source]}), encoding="utf-8")
    return path


def test_valid_manifest_loads(tmp_path: Path) -> None:
    manifest = load_manifest(write_manifest(tmp_path / "sources.yml", valid_source()))
    assert manifest.sources[0].source_id == "example-source"
    assert manifest.sources[0].classification_rank == 0


def test_missing_sha256_is_rejected(tmp_path: Path) -> None:
    source = deepcopy(valid_source())
    del source["sha256"]
    with pytest.raises(ValidationError, match="sha256"):
        load_manifest(write_manifest(tmp_path / "sources.yml", source))


def test_unapproved_source_is_preserved_for_later_rejection(tmp_path: Path) -> None:
    source = deepcopy(valid_source())
    source["approved"] = False
    source["approved_by"] = None
    source["approved_at"] = None
    manifest = load_manifest(write_manifest(tmp_path / "sources.yml", source))
    assert manifest.sources[0].approved is False
    assert manifest.sources[0].approved_by is None
    assert manifest.sources[0].approved_at is None


def test_invalid_tenant_is_rejected(tmp_path: Path) -> None:
    source = deepcopy(valid_source())
    source["tenant"] = "another-tenant"
    with pytest.raises(ValidationError, match="portfolio-demo"):
        load_manifest(write_manifest(tmp_path / "sources.yml", source))


def test_unsupported_classification_is_rejected(tmp_path: Path) -> None:
    source = deepcopy(valid_source())
    source["classification"] = "confidential"
    with pytest.raises(ValidationError, match="classification"):
        load_manifest(write_manifest(tmp_path / "sources.yml", source))


def test_path_cannot_escape_data_root(tmp_path: Path) -> None:
    source = deepcopy(valid_source())
    source["local_relative_path"] = "../outside.txt"
    manifest = load_manifest(write_manifest(tmp_path / "sources.yml", source))
    with pytest.raises(ValueError, match="escapes"):
        manifest.sources[0].resolve_local_path(tmp_path)
