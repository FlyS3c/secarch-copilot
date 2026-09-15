"""Tests for local API authentication and trusted user context."""

from typing import Annotated

import pytest
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

from app.api.dependencies import get_user_context
from app.core.auth import UserContext
from app.core.settings import settings

TEST_API_KEY = "synthetic-test-api-key-at-least-24-characters"

authentication_app = FastAPI()


@authentication_app.get("/protected")
def protected_route(
    context: Annotated[
        UserContext,
        Depends(get_user_context),
    ],
) -> dict[str, str | int]:
    """Return the trusted context for unit-test verification."""

    return {
        "tenant": context.tenant,
        "role": context.role,
        "clearance_rank": context.clearance_rank,
    }


@pytest.fixture
def client(monkeypatch) -> TestClient:
    """Create a test client using synthetic trusted settings."""

    monkeypatch.setattr(
        settings,
        "secarch_local_api_key",
        TEST_API_KEY,
    )
    monkeypatch.setattr(
        settings,
        "secarch_tenant",
        "portfolio-demo",
    )
    monkeypatch.setattr(
        settings,
        "secarch_role",
        "security-architect",
    )

    return TestClient(authentication_app)


def test_correct_api_key_is_accepted(client: TestClient) -> None:
    response = client.get(
        "/protected",
        headers={"X-API-Key": TEST_API_KEY},
    )

    assert response.status_code == 200
    assert response.json() == {
        "tenant": "portfolio-demo",
        "role": "security-architect",
        "clearance_rank": 1,
    }


def test_incorrect_api_key_is_rejected(client: TestClient) -> None:
    response = client.get(
        "/protected",
        headers={"X-API-Key": "incorrect-test-key"},
    )

    assert response.status_code == 401
    assert response.json() == {
        "detail": "Invalid credentials",
    }


def test_missing_api_key_is_rejected(client: TestClient) -> None:
    response = client.get("/protected")

    assert response.status_code == 401
    assert response.json() == {
        "detail": "Invalid credentials",
    }


def test_caller_cannot_override_context(client: TestClient) -> None:
    response = client.get(
        "/protected?tenant=another-tenant&role=administrator",
        headers={"X-API-Key": TEST_API_KEY},
    )

    assert response.status_code == 200
    assert response.json()["tenant"] == "portfolio-demo"
    assert response.json()["role"] == "security-architect"
    assert response.json()["clearance_rank"] == 1
