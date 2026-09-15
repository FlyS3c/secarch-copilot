"""Tests for privacy-safe audit events."""

import json
from datetime import datetime, timezone
from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.core.audit import AuditEvent, write_audit_event


def build_event() -> AuditEvent:
    return AuditEvent(
        request_id=uuid4(),
        timestamp_utc=datetime.now(timezone.utc),
        workflow="architecture_review",
        tenant="portfolio-demo",
        role="security-architect",
        policy_decision="allowed",
        source_ids=["nist-ai-600-1"],
        retrieved_chunk_count=1,
        latency_ms=1250,
        result="success",
        error_category=None,
    )


def test_audit_event_is_written_as_jsonl(tmp_path) -> None:
    log_path = tmp_path / "audit.jsonl"
    event = build_event()

    returned_path = write_audit_event(event, log_path)

    lines = log_path.read_text(encoding="utf-8").splitlines()
    saved_event = json.loads(lines[0])

    assert returned_path == log_path
    assert len(lines) == 1
    assert saved_event["workflow"] == "architecture_review"
    assert saved_event["source_ids"] == ["nist-ai-600-1"]
    assert saved_event["retrieved_chunk_count"] == 1


def test_audit_events_are_appended(tmp_path) -> None:
    log_path = tmp_path / "audit.jsonl"

    write_audit_event(build_event(), log_path)
    write_audit_event(build_event(), log_path)

    lines = log_path.read_text(encoding="utf-8").splitlines()

    assert len(lines) == 2


def test_sensitive_extra_fields_are_rejected() -> None:
    event_data = build_event().model_dump()
    event_data["raw_prompt"] = "synthetic-canary-secret"

    with pytest.raises(ValidationError):
        AuditEvent.model_validate(event_data)
