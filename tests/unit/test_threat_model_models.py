"""Tests for structured threat-model responses."""

import pytest
from pydantic import ValidationError

from app.models.responses import Citation, Threat, ThreatModel


def valid_threat() -> Threat:
    return Threat(
        threat_id="TM-01",
        category="spoofing",
        threat="An attacker could impersonate a legitimate user.",
        affected_assets=["Synthetic customer records"],
        severity="high",
        mitigation="Require phishing-resistant multifactor authentication.",
        residual_risk="Stolen authenticated sessions remain possible.",
        citations=[
            Citation(
                source_id="nist-sp-800-207",
                chunk_id="nist-sp-800-207-example",
                page_or_section="page 10",
            )
        ],
    )


def valid_threat_model() -> ThreatModel:
    return ThreatModel(
        summary="The fictional application has several identity-related risks.",
        assumptions=["The identity provider supports multifactor authentication."],
        missing_information=["Session-management details were not provided."],
        assets=["Synthetic customer records", "User identities"],
        trust_boundaries=["Internet to web application"],
        threats=[valid_threat()],
        residual_risk_questions=[
            "How are compromised authenticated sessions detected?"
        ],
        limitations=["This is a draft requiring human validation."],
    )


def test_valid_threat_model_is_accepted() -> None:
    result = valid_threat_model()

    assert result.threats[0].category == "spoofing"
    assert result.threats[0].human_review_required is True


def test_unknown_threat_category_is_rejected() -> None:
    data = valid_threat().model_dump()
    data["category"] = "unknown-category"

    with pytest.raises(ValidationError):
        Threat.model_validate(data)


def test_more_than_fifteen_threats_are_rejected() -> None:
    data = valid_threat_model().model_dump()
    data["threats"] = [valid_threat().model_dump() for _ in range(16)]

    with pytest.raises(ValidationError):
        ThreatModel.model_validate(data)


def test_unexpected_output_field_is_rejected() -> None:
    data = valid_threat_model().model_dump()
    data["architecture_approved"] = True

    with pytest.raises(ValidationError):
        ThreatModel.model_validate(data)
