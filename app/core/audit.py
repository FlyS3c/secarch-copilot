"""Privacy-safe JSONL audit events."""

from datetime import datetime
from pathlib import Path
from threading import Lock
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.core.settings import settings


class AuditEvent(BaseModel):
    """Metadata allowed in one audit event."""

    model_config = ConfigDict(extra="forbid")

    request_id: UUID
    timestamp_utc: datetime
    workflow: Literal[
        "architecture_review",
        "threat_model",
        "authentication",
    ]
    tenant: str = Field(min_length=1, max_length=100)
    role: str = Field(min_length=1, max_length=100)
    policy_decision: Literal["allowed", "denied"]
    source_ids: list[str] = Field(
        default_factory=list,
        max_length=20,
    )
    retrieved_chunk_count: int = Field(ge=0, le=8)
    latency_ms: int = Field(ge=0)
    result: Literal["success", "abstained", "error"]
    error_category: str | None = Field(
        default=None,
        max_length=100,
    )


_AUDIT_LOCK = Lock()


def write_audit_event(
    event: AuditEvent,
    log_path: Path | None = None,
) -> Path:
    """Append one validated audit event as a JSON line."""

    destination = log_path or settings.audit_log_path
    destination.parent.mkdir(parents=True, exist_ok=True)

    serialized_event = event.model_dump_json()

    with (
        _AUDIT_LOCK,
        destination.open(
            mode="a",
            encoding="utf-8",
        ) as audit_file,
    ):
        audit_file.write(serialized_event)
        audit_file.write("\n")

    return destination
