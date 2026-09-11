"""Tests for structured Ollama architecture-review generation."""

import json
from types import SimpleNamespace

import pytest
from pydantic import ValidationError

from app.workflows.architecture_review import generate_review


def valid_response() -> dict:
    """Return a valid synthetic model response."""

    return {
        "summary": "The fictional design requires stronger access controls.",
        "assumptions": [
            "The storage service is reachable from the internet."
        ],
        "missing_information": [
            "The identity-provider configuration was not supplied."
        ],
        "findings": [
            {
                "finding_id": "F-001",
                "risk": (
                    "Administrative access does not require "
                    "multifactor authentication."
                ),
                "severity": "high",
                "recommendation": (
                    "Require multifactor authentication for all "
                    "administrative access."
                ),
                "citations": [
                    {
                        "source_id": "nist-sp-800-53-rev5",
                        "chunk_id": "chunk-001",
                        "page_or_section": "page 341",
                    }
                ],
                "human_review_required": True,
            }
        ],
        "limitations": [
            "The recommendation requires human review."
        ],
    }


def test_generate_review_uses_schema(monkeypatch) -> None:
    captured_arguments = {}

    def fake_chat(**kwargs):
        captured_arguments.update(kwargs)

        return SimpleNamespace(
            message=SimpleNamespace(
                content=json.dumps(valid_response())
            )
        )

    monkeypatch.setattr(
        "app.workflows.architecture_review.chat",
        fake_chat,
    )

    review = generate_review("Review this synthetic architecture.")

    assert review.findings[0].finding_id == "F-001"
    assert review.findings[0].severity == "high"
    assert captured_arguments["model"] == "llama3.2:3b"
    assert captured_arguments["options"]["temperature"] == 0
    assert captured_arguments["format"] is not None


def test_invalid_model_response_is_rejected(monkeypatch) -> None:
    invalid_response = valid_response()
    invalid_response["findings"][0]["severity"] = "critical"

    def fake_chat(**kwargs):
        return SimpleNamespace(
            message=SimpleNamespace(
                content=json.dumps(invalid_response)
            )
        )

    monkeypatch.setattr(
        "app.workflows.architecture_review.chat",
        fake_chat,
    )

    with pytest.raises(ValidationError):
        generate_review("Review this synthetic architecture.")


def test_empty_prompt_is_rejected() -> None:
    with pytest.raises(ValueError, match="Prompt cannot be empty"):
        generate_review("   ")