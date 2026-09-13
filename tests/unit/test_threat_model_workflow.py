"""Tests for structured Ollama threat-model generation."""

import json
from types import SimpleNamespace

import pytest
from pydantic import ValidationError

from app.models.requests import ThreatModelRequest
from app.models.responses import ThreatModel
from app.workflows.threat_model import (
    build_threat_model_description,
    generate_threat_model,
    validate_threat_citations,
)


def valid_response() -> dict:
    """Return a valid synthetic threat-model response."""

    return {
        "summary": (
            "The fictional application has identity and access risks."
        ),
        "assumptions": [
            "The identity provider supports multifactor authentication."
        ],
        "missing_information": [
            "Session-management details were not supplied."
        ],
        "assets": [
            "Synthetic customer records",
            "User identities",
        ],
        "trust_boundaries": [
            "Internet to web application",
        ],
        "threats": [
            {
                "threat_id": "TM-001",
                "category": "spoofing",
                "threat": (
                    "An attacker could impersonate a legitimate user."
                ),
                "affected_assets": [
                    "User identities",
                ],
                "severity": "high",
                "mitigation": (
                    "Require phishing-resistant multifactor "
                    "authentication."
                ),
                "residual_risk": (
                    "Authenticated sessions could still be stolen."
                ),
                "citations": [
                    {
                        "source_id": "nist-sp-800-207",
                        "chunk_id": "chunk-001",
                        "page_or_section": "page 10",
                    }
                ],
                "human_review_required": True,
            }
        ],
        "residual_risk_questions": [
            "How are compromised sessions detected?"
        ],
        "limitations": [
            "The threat model requires human review."
        ],
    }


def test_generate_threat_model_uses_schema(monkeypatch) -> None:
    captured_arguments = {}

    def fake_chat(**kwargs):
        captured_arguments.update(kwargs)

        return SimpleNamespace(
            message=SimpleNamespace(
                content=json.dumps(valid_response())
            )
        )

    monkeypatch.setattr(
        "app.workflows.threat_model.chat",
        fake_chat,
    )

    threat_model = generate_threat_model(
        "Threat model this synthetic architecture."
    )

    assert threat_model.threats[0].threat_id == "TM-001"
    assert threat_model.threats[0].category == "spoofing"
    assert captured_arguments["model"] == "llama3.2:3b"
    assert captured_arguments["options"]["temperature"] == 0
    assert captured_arguments["format"] is not None


def test_invalid_model_response_is_rejected(
    monkeypatch,
) -> None:
    invalid_response = valid_response()
    invalid_response["threats"][0]["category"] = "unknown"

    def fake_chat(**kwargs):
        return SimpleNamespace(
            message=SimpleNamespace(
                content=json.dumps(invalid_response)
            )
        )

    monkeypatch.setattr(
        "app.workflows.threat_model.chat",
        fake_chat,
    )

    with pytest.raises(ValidationError):
        generate_threat_model(
            "Threat model this synthetic architecture."
        )


def test_empty_prompt_is_rejected() -> None:
    with pytest.raises(
        ValueError,
        match="Prompt cannot be empty",
    ):
        generate_threat_model("   ")


def test_description_includes_data_flows() -> None:
    request = ThreatModelRequest(
        system_name="Synthetic Portal",
        purpose=(
            "Provide fictional users access to synthetic records."
        ),
        components=[
            "Web application",
            "REST API",
            "Storage",
        ],
        data_classes=["Synthetic customer records"],
        identities=["Customer", "Administrator"],
        integrations=["Synthetic identity provider"],
        network_boundaries=["Internet to application"],
        data_flows=[
            "Browser to web application",
            "Web application to API",
            "API to storage",
        ],
    )

    description = build_threat_model_description(request)

    assert (
        "Data flows: Browser to web application; "
        "Web application to API; API to storage"
        in description
    )


def test_allowed_threat_citation_is_accepted() -> None:
    threat_model = ThreatModel.model_validate(
        valid_response()
    )

    chunks = [
        SimpleNamespace(
            source_id="nist-sp-800-207",
            chunk_id="chunk-001",
            page_or_section="page 10",
        )
    ]

    validate_threat_citations(threat_model, chunks)


def test_unsupported_threat_citation_is_rejected() -> None:
    threat_model = ThreatModel.model_validate(
        valid_response()
    )

    chunks = [
        SimpleNamespace(
            source_id="different-source",
            chunk_id="different-chunk",
            page_or_section="page 99",
        )
    ]

    with pytest.raises(
        ValueError,
        match="unsupported citation",
    ):
        validate_threat_citations(
            threat_model,
            chunks,
        )