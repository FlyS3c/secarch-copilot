from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

from app.ingestion.manifest import SourceRecord
from app.ingestion.validators import (
    SourceValidationError,
    quarantine_source_file,
    validate_extracted_text,
    validate_source_file,
)


def source_for(path: Path, content: bytes, *, approved: bool = True) -> SourceRecord:
    return SourceRecord(
        source_id="fixture-source",
        title="Fixture",
        publisher="Portfolio Test",
        version="1",
        official_url="https://example.com",
        retrieval_url="https://example.com/fixture.txt",
        license_name="Synthetic fixture",
        retrieved_at="2026-09-08",
        local_relative_path=path.as_posix(),
        file_type="txt",
        sha256=hashlib.sha256(content).hexdigest(),
        tenant="portfolio-demo",
        allowed_roles=["security-architect"],
        classification="internal-demo",
        approved=approved,
        approved_by="Glenn Merritt" if approved else None,
        approved_at="2026-09-08" if approved else None,
    )


def test_valid_file_passes_checksum(tmp_path: Path) -> None:
    relative = Path("raw/fixture.txt")
    path = tmp_path / relative
    path.parent.mkdir(parents=True)
    content = b"Synthetic architecture text"
    path.write_bytes(content)

    result = validate_source_file(source_for(relative, content), tmp_path)
    assert result.path == path.resolve()


def test_modified_file_is_rejected_and_quarantined(
    tmp_path: Path,
) -> None:
    relative = Path("raw/fixture.txt")
    path = tmp_path / relative
    path.parent.mkdir(parents=True)
    path.write_bytes(b"modified")

    source = source_for(relative, b"original")

    with pytest.raises(
        SourceValidationError,
        match="SHA-256 mismatch",
    ) as error:
        validate_source_file(source, tmp_path)

    quarantined_path = quarantine_source_file(
        source,
        tmp_path,
        reason=str(error.value),
    )

    reason_path = quarantined_path.with_name(f"{quarantined_path.name}.reason.txt")

    assert not path.exists()
    assert quarantined_path.is_file()
    assert quarantined_path.read_bytes() == b"modified"
    assert "SHA-256 mismatch" in reason_path.read_text(encoding="utf-8")


def test_unsupported_file_type_is_rejected_and_quarantined(
    tmp_path: Path,
) -> None:
    relative = Path("raw/fixture.exe")
    path = tmp_path / relative
    path.parent.mkdir(parents=True)
    content = b"synthetic executable content"
    path.write_bytes(content)

    source = source_for(relative, content).model_copy(
        update={
            "file_type": "exe",
        }
    )

    with pytest.raises(
        SourceValidationError,
        match="unsupported file type",
    ) as error:
        validate_source_file(source, tmp_path)

    quarantined_path = quarantine_source_file(
        source,
        tmp_path,
        reason=str(error.value),
    )

    assert not path.exists()
    assert quarantined_path.is_file()
    assert quarantined_path.read_bytes() == content
    assert quarantined_path.parent.name == "fixture-source"
    assert quarantined_path.parent.parent.name == "quarantine"


def test_private_key_is_rejected() -> None:
    text = "-----BEGIN PRIVATE KEY-----\nnot-a-real-key"
    with pytest.raises(SourceValidationError, match="private key"):
        validate_extracted_text(text)


def test_instruction_text_generates_review_warning() -> None:
    warnings = validate_extracted_text(
        "A malicious document might say: ignore previous instructions."
    )
    assert any("instruction-like text" in warning for warning in warnings)
