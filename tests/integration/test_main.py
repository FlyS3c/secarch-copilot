"""Integration tests for the initial FastAPI routes."""

from fastapi.testclient import TestClient

from app.core.settings import settings
from app.main import app
from app.models.responses import ArchitectureReview, ThreatModel

TEST_API_KEY = "synthetic-integration-key-at-least-24-characters"


def valid_payload() -> dict:
    return {
        "system_name": "Synthetic Portal",
        "purpose": (
            "Provide fictional users with access to synthetic account information."
        ),
        "components": ["Web application", "API"],
        "data_classes": ["Synthetic data"],
        "identities": ["Customer", "Administrator"],
        "integrations": ["Synthetic identity provider"],
        "network_boundaries": ["Internet to application"],
    }


def valid_threat_model_payload() -> dict:
    return {
        **valid_payload(),
        "data_flows": [
            "Browser to web application",
            "Web application to API",
        ],
    }


def synthetic_review() -> ArchitectureReview:
    return ArchitectureReview.model_validate(
        {
            "summary": "Synthetic architecture review completed.",
            "assumptions": [],
            "missing_information": [],
            "findings": [],
            "limitations": ["Human review is required."],
        }
    )


def synthetic_threat_model() -> ThreatModel:
    return ThreatModel.model_validate(
        {
            "summary": "Synthetic threat model completed.",
            "assumptions": [],
            "missing_information": [],
            "assets": ["Synthetic customer data"],
            "trust_boundaries": [
                "Internet to web application",
            ],
            "threats": [],
            "residual_risk_questions": ["How are authenticated sessions monitored?"],
            "limitations": ["Human review is required."],
        }
    )


def test_health_route() -> None:
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_architecture_route_requires_key(monkeypatch) -> None:
    monkeypatch.setattr(
        settings,
        "secarch_local_api_key",
        TEST_API_KEY,
    )

    client = TestClient(app)
    response = client.post(
        "/v1/architecture-review",
        json=valid_payload(),
    )

    assert response.status_code == 401


def test_architecture_route_rejects_wrong_key(
    monkeypatch,
) -> None:
    monkeypatch.setattr(
        settings,
        "secarch_local_api_key",
        TEST_API_KEY,
    )

    client = TestClient(app)
    response = client.post(
        "/v1/architecture-review",
        headers={"X-API-Key": "wrong-key"},
        json=valid_payload(),
    )

    assert response.status_code == 401


def test_architecture_route_returns_review(
    monkeypatch,
) -> None:
    monkeypatch.setattr(
        settings,
        "secarch_local_api_key",
        TEST_API_KEY,
    )

    def fake_run_architecture_review(
        request,
        context,
        request_id,
        audit_log_path,
    ):
        assert context.tenant == "portfolio-demo"
        assert context.role == "security-architect"
        assert request_id
        assert audit_log_path == settings.audit_log_path

        return synthetic_review()

    monkeypatch.setattr(
        "app.main.run_architecture_review",
        fake_run_architecture_review,
    )

    client = TestClient(app)
    response = client.post(
        "/v1/architecture-review",
        headers={"X-API-Key": TEST_API_KEY},
        json=valid_payload(),
    )

    assert response.status_code == 200
    assert response.json()["summary"] == ("Synthetic architecture review completed.")


def test_threat_model_route_requires_key(
    monkeypatch,
) -> None:
    monkeypatch.setattr(
        settings,
        "secarch_local_api_key",
        TEST_API_KEY,
    )

    client = TestClient(app)
    response = client.post(
        "/v1/threat-model",
        json=valid_threat_model_payload(),
    )

    assert response.status_code == 401


def test_threat_model_route_returns_model(
    monkeypatch,
) -> None:
    monkeypatch.setattr(
        settings,
        "secarch_local_api_key",
        TEST_API_KEY,
    )

    def fake_run_threat_model(
        request,
        context,
        request_id,
        audit_log_path,
    ):
        assert context.tenant == "portfolio-demo"
        assert context.role == "security-architect"
        assert request.data_flows == [
            "Browser to web application",
            "Web application to API",
        ]
        assert request_id
        assert audit_log_path == settings.audit_log_path

        return synthetic_threat_model()

    monkeypatch.setattr(
        "app.main.run_threat_model",
        fake_run_threat_model,
    )

    client = TestClient(app)
    response = client.post(
        "/v1/threat-model",
        headers={"X-API-Key": TEST_API_KEY},
        json=valid_threat_model_payload(),
    )

    assert response.status_code == 200
    assert response.json()["summary"] == ("Synthetic threat model completed.")
    assert response.json()["assets"] == ["Synthetic customer data"]


def test_threat_model_cannot_select_identity(
    monkeypatch,
) -> None:
    monkeypatch.setattr(
        settings,
        "secarch_local_api_key",
        TEST_API_KEY,
    )

    payload = valid_threat_model_payload()
    payload["tenant"] = "another-tenant"
    payload["role"] = "administrator"
    payload["clearance_rank"] = 999

    client = TestClient(app)
    response = client.post(
        "/v1/threat-model",
        headers={"X-API-Key": TEST_API_KEY},
        json=payload,
    )

    assert response.status_code == 422
