"""Load and validate the tracked source manifest."""

from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

Classification = Literal["public", "internal-demo", "restricted"]
Role = Literal["security-architect", "security-engineer", "viewer"]
FileType = Literal["pdf", "docx", "markdown", "txt"]

CLASSIFICATION_RANKS: dict[str, int] = {
    "public": 0,
    "internal-demo": 1,
    "restricted": 2,
}


class SourceRecord(BaseModel):
    """One explicitly approved or rejected source in data/sources.yml."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    source_id: str = Field(pattern=r"^[a-z0-9-]+$")
    title: str = Field(min_length=1)
    publisher: str = Field(min_length=1)
    version: str = Field(min_length=1)
    official_url: str = Field(min_length=1)
    retrieval_url: str = Field(min_length=1)
    license_name: str = Field(min_length=1)
    license_url: str | None = None
    retrieved_at: date
    local_relative_path: str = Field(min_length=1)
    file_type: FileType
    sha256: str = Field(pattern=r"^[A-Fa-f0-9]{64}$")
    tenant: Literal["portfolio-demo"]
    allowed_roles: list[Role] = Field(min_length=1)
    classification: Classification
    approved: bool
    approved_by: str | None = None
    approved_at: date | None = None
    notes: str = ""

    @field_validator("sha256")
    @classmethod
    def normalize_sha256(cls, value: str) -> str:
        return value.lower()

    @field_validator("allowed_roles")
    @classmethod
    def roles_must_be_unique(cls, value: list[Role]) -> list[Role]:
        if len(value) != len(set(value)):
            raise ValueError("allowed_roles cannot contain duplicates")
        return value

    @model_validator(mode="after")
    def approved_sources_need_approval_evidence(self) -> SourceRecord:
        if self.approved and (not self.approved_by or self.approved_at is None):
            raise ValueError("approved=true requires approved_by and approved_at")
        return self

    @property
    def classification_rank(self) -> int:
        """Convert the classification label into a numeric clearance rank."""
        return CLASSIFICATION_RANKS[self.classification]

    def resolve_local_path(self, data_root: Path) -> Path:
        """Resolve the source path and prevent escape from SECARCH_DATA_ROOT."""
        root = data_root.expanduser().resolve()
        relative = Path(self.local_relative_path)
        if relative.is_absolute():
            raise ValueError(f"{self.source_id}: local_relative_path must be relative")

        candidate = (root / relative).resolve()
        if not candidate.is_relative_to(root):
            raise ValueError(f"{self.source_id}: local path escapes SECARCH_DATA_ROOT")
        return candidate


class SourceManifest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version: Literal[1] = 1
    sources: list[SourceRecord] = Field(min_length=1)

    @model_validator(mode="after")
    def source_ids_must_be_unique(self) -> SourceManifest:
        source_ids = [source.source_id for source in self.sources]
        if len(source_ids) != len(set(source_ids)):
            raise ValueError("Manifest contains duplicate source_id values")
        return self


def load_manifest(path: Path) -> SourceManifest:
    """Read YAML safely and validate every manifest field."""
    if not path.is_file():
        raise FileNotFoundError(f"Manifest not found: {path}")

    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise ValueError(f"Invalid YAML in {path}: {exc}") from exc

    if raw is None:
        raise ValueError(f"Manifest is empty: {path}")

    return SourceManifest.model_validate(raw)
