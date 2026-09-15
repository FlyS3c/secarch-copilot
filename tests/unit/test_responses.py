"""Tests for structured architecture-review responses."""

import pytest
from pydantic import ValidationError

from app.models.responses import ArchitectureReview


def valid_finding(number: int = 1) -> dict:
    """Return one valid synthetic finding."""

    return {
        "finding_id": f"F-{number:03d}",
        "risk": "Administrative access does not require multifactor authentication.",
        "severity": "high",
        "recommendation": (
            "Require phishing-resistant multifactor authentication "
            "for administrative access."
        ),
        "citations": [
            {
                "source_id": "nist-sp-800-53-rev5",
                "chunk_id": "nist-sp-800-53-rev5-example",
                "page_or_section": "page 341",
            }
        ],
    }


def valid_review() -> dict:
    """Return a complete valid synthetic architecture review."""

    return {
        "summary": "The proposed architecture requires additional access controls.",
        "assumptions": ["The system is accessible only to authorized employees."],
        "missing_information": [
            "The identity provider configuration was not supplied."
        ],
        "findings": [valid_finding()],
        "limitations": ["This is an advisory review and requires human validation."],
    }


def test_valid_architecture_review_is_accepted() -> None:
    review = ArchitectureReview.model_validate(valid_review())

    assert review.summary.startswith("The proposed architecture")
    assert len(review.findings) == 1
    assert review.findings[0].severity == "high"
    assert review.findings[0].human_review_required is True
    assert review.findings[0].citations[0].source_id == "nist-sp-800-53-rev5"


def test_invalid_severity_is_rejected() -> None:
    payload = valid_review()
    payload["findings"][0]["severity"] = "critical"

    with pytest.raises(ValidationError):
        ArchitectureReview.model_validate(payload)


def test_unexpected_field_is_rejected() -> None:
    payload = valid_review()
    payload["approval_status"] = "approved"

    with pytest.raises(ValidationError):
        ArchitectureReview.model_validate(payload)


def test_more_than_ten_findings_is_rejected() -> None:
    payload = valid_review()
    payload["findings"] = [valid_finding(number) for number in range(1, 12)]

    with pytest.raises(ValidationError):
        ArchitectureReview.model_validate(payload)


def test_invalid_finding_id_is_rejected() -> None:
    payload = valid_review()
    payload["findings"][0]["finding_id"] = "EVIDENCE_1"

    with pytest.raises(ValidationError):
        ArchitectureReview.model_validate(payload)


def test_severity_label_is_rejected_as_risk() -> None:
    payload = valid_review()
    payload["findings"][0]["risk"] = "High"

    with pytest.raises(ValidationError):
        ArchitectureReview.model_validate(payload)


def test_human_review_cannot_be_disabled() -> None:
    payload = valid_review()
    payload["findings"][0]["human_review_required"] = False

    with pytest.raises(ValidationError):
        ArchitectureReview.model_validate(payload)
