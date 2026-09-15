"""Fail-closed validation for files and extracted document text."""

from __future__ import annotations

import hashlib
import re
import zipfile
from dataclasses import dataclass, field
from pathlib import Path, PurePosixPath

from app.ingestion.manifest import SourceManifest, SourceRecord

ALLOWED_SUFFIXES = {
    "pdf": ".pdf",
    "docx": ".docx",
    "markdown": ".md",
    "txt": ".txt",
}
DEFAULT_MAX_FILE_BYTES = 25 * 1024 * 1024
DEFAULT_MAX_DOCX_UNCOMPRESSED_BYTES = 100 * 1024 * 1024

BLOCKING_CONTENT_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    (
        "private key",
        re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    ),
    ("AWS access key", re.compile(r"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b")),
    ("U.S. Social Security number", re.compile(r"\b\d{3}-\d{2}-\d{4}\b")),
)

REVIEW_CONTENT_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    (
        "instruction-like text",
        re.compile(
            r"\b(?:ignore|disregard|override)\s+(?:all\s+)?(?:previous|prior|system)\s+instructions?\b",
            re.IGNORECASE,
        ),
    ),
    (
        "prompt or role marker",
        re.compile(
            r"\b(?:system prompt|developer message|assistant role)\b", re.IGNORECASE
        ),
    ),
    (
        "email address",
        re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE),
    ),
)


class SourceValidationError(ValueError):
    """Raised when a source must not proceed to parsing or indexing."""


@dataclass(slots=True)
class ValidationResult:
    source: SourceRecord
    path: Path
    warnings: list[str] = field(default_factory=list)


def sha256_file(path: Path, block_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while block := stream.read(block_size):
            digest.update(block)
    return digest.hexdigest()


def validate_manifest_uniqueness(manifest: SourceManifest) -> None:
    """Reject duplicate document content registered under different IDs."""
    seen_hashes: dict[str, str] = {}
    for source in manifest.sources:
        previous_id = seen_hashes.get(source.sha256)
        if previous_id is not None and previous_id != source.source_id:
            raise SourceValidationError(
                f"Duplicate SHA-256: {source.source_id} and {previous_id}"
            )
        seen_hashes[source.sha256] = source.source_id


def _validate_docx_archive(path: Path) -> None:
    if not zipfile.is_zipfile(path):
        raise SourceValidationError(f"Malformed DOCX file: {path}")

    total_uncompressed = 0
    with zipfile.ZipFile(path) as archive:
        for member in archive.infolist():
            member_path = PurePosixPath(member.filename)
            if member_path.is_absolute() or ".." in member_path.parts:
                raise SourceValidationError(
                    f"Unsafe path inside DOCX archive: {member.filename}"
                )
            total_uncompressed += member.file_size
            if total_uncompressed > DEFAULT_MAX_DOCX_UNCOMPRESSED_BYTES:
                raise SourceValidationError(
                    f"DOCX expands beyond {DEFAULT_MAX_DOCX_UNCOMPRESSED_BYTES} bytes"
                )


def validate_source_file(
    source: SourceRecord,
    data_root: Path,
    *,
    max_file_bytes: int = DEFAULT_MAX_FILE_BYTES,
) -> ValidationResult:
    """Validate approval, path, type, size, archive safety, and checksum."""
    if not source.approved:
        raise SourceValidationError(f"{source.source_id}: approved is not true")

    try:
        path = source.resolve_local_path(data_root)
    except ValueError as exc:
        raise SourceValidationError(str(exc)) from exc

    if not path.is_file():
        raise SourceValidationError(f"{source.source_id}: file not found: {path}")

    expected_suffix = ALLOWED_SUFFIXES.get(source.file_type)
    if expected_suffix is None:
        raise SourceValidationError(
            f"{source.source_id}: unsupported file type: {source.file_type}"
        )

    file_size = path.stat().st_size
    if file_size == 0:
        raise SourceValidationError(f"{source.source_id}: file is empty")
    if file_size > max_file_bytes:
        raise SourceValidationError(
            f"{source.source_id}: file is {file_size} bytes; limit is {max_file_bytes}"
        )

    if source.file_type == "docx":
        _validate_docx_archive(path)

    actual_sha256 = sha256_file(path)
    if actual_sha256 != source.sha256:
        raise SourceValidationError(
            f"{source.source_id}: SHA-256 mismatch; "
            f"expected {source.sha256}, got {actual_sha256}"
        )

    return ValidationResult(source=source, path=path)


def quarantine_source_file(
    source: SourceRecord,
    data_root: Path,
    *,
    reason: str,
) -> Path:
    """Move an invalid source into an isolated quarantine directory."""
    try:
        source_path = source.resolve_local_path(data_root)
    except ValueError as exc:
        raise SourceValidationError(
            f"{source.source_id}: cannot quarantine an unsafe path"
        ) from exc

    if not source_path.is_file():
        raise SourceValidationError(
            f"{source.source_id}: quarantine source not found: {source_path}"
        )

    safe_source_id = re.sub(
        r"[^A-Za-z0-9._-]",
        "_",
        source.source_id,
    ).strip("._")

    if not safe_source_id:
        safe_source_id = "unknown-source"

    quarantine_directory = (data_root / "quarantine" / safe_source_id).resolve()
    quarantine_directory.mkdir(parents=True, exist_ok=True)

    destination = quarantine_directory / source_path.name
    sequence = 1

    while destination.exists():
        destination = quarantine_directory / (
            f"{source_path.stem}-{sequence}{source_path.suffix}"
        )
        sequence += 1

    source_path.replace(destination)

    reason_path = destination.with_name(f"{destination.name}.reason.txt")
    reason_path.write_text(
        reason.strip() or "Unspecified validation failure",
        encoding="utf-8",
    )

    return destination


def validate_extracted_text(text: str) -> list[str]:
    """Block high-confidence secrets/PII and flag instructions for review."""
    if not text.strip():
        raise SourceValidationError("Parsed document contains no text")

    blocking_findings = [
        name for name, pattern in BLOCKING_CONTENT_PATTERNS if pattern.search(text)
    ]
    if blocking_findings:
        raise SourceValidationError(
            "Sensitive content detected: " + ", ".join(blocking_findings)
        )

    return [
        f"Review required: detected {name}"
        for name, pattern in REVIEW_CONTENT_PATTERNS
        if pattern.search(text)
    ]
