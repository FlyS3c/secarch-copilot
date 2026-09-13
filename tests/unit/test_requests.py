"""Tests for workflow request models."""

import pytest
from pydantic import ValidationError

from app.models.requests import (
    ArchitectureReviewRequest,
    ThreatModelRequest,
)


def valid_request() -> dict:
    """Return a valid synthetic architecture description."""

    return {
        "system_name": "Synthetic Customer Portal",
        "purpose": (
            "Provide fictional customers with access to public "
            "account-management features."
        ),
        "components": [
            "Web application",
            "API",
            "Azure Blob Storage",
        ],
        "data_classes": [
            "Public",
            "Synthetic customer information",
        ],
        "identities": [
            "Customer",
            "Administrator",
            "Managed identity",
        ],
        "integrations": [
            "Synthetic identity provider",
        ],
        "network_boundaries": [
            "Internet to web application",
            "Application network to storage network",
        ],
    }


def test_valid_architecture_request_is_accepted() -> None:
    request = ArchitectureReviewRequest.model_validate(
        valid_request()
    )

    assert request.system_name == "Synthetic Customer Portal"
    assert len(request.components) == 3
    assert request.integrations == ["Synthetic identity provider"]


def test_authorization_fields_are_rejected() -> None:
    authorization_fields = {
        "tenant": "another-tenant",
        "role": "administrator",
        "clearance_rank": 99,
        "approved": True,
    }

    for field_name, field_value in authorization_fields.items():
        payload = valid_request()
        payload[field_name] = field_value

        with pytest.raises(ValidationError):
            ArchitectureReviewRequest.model_validate(payload)


def test_short_purpose_is_rejected() -> None:
    payload = valid_request()
    payload["purpose"] = "Too short"

    with pytest.raises(ValidationError):
        ArchitectureReviewRequest.model_validate(payload)


def test_empty_components_are_rejected() -> None:
    payload = valid_request()
    payload["components"] = []

    with pytest.raises(ValidationError):
        ArchitectureReviewRequest.model_validate(payload)


def test_too_many_components_are_rejected() -> None:
    payload = valid_request()
    payload["components"] = [
        f"Synthetic component {number}"
        for number in range(31)
    ]

    with pytest.raises(ValidationError):
        ArchitectureReviewRequest.model_validate(payload)


def test_threat_model_accepts_data_flows() -> None:
    payload = valid_request()
    payload["data_flows"] = [
        "Customer browser sends a request to the web application.",
        "Web application sends an authorized request to the API.",
        "API retrieves synthetic records from storage.",
    ]

    request = ThreatModelRequest.model_validate(payload)

    assert len(request.data_flows) == 3
    assert request.system_name == "Synthetic Customer Portal"