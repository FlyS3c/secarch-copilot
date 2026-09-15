"""Tests for API resource-limit middleware."""

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.limits import (
    LocalRateLimitMiddleware,
    RequestBodyLimitMiddleware,
)


def build_test_app(
    body_limit: int = 1_024,
    rate_limit: int = 10,
) -> FastAPI:
    test_application = FastAPI()

    test_application.add_middleware(
        LocalRateLimitMiddleware,
        max_requests=rate_limit,
        window_seconds=60,
    )

    test_application.add_middleware(
        RequestBodyLimitMiddleware,
        max_body_bytes=body_limit,
    )

    @test_application.post("/v1/test")
    def test_endpoint(payload: dict) -> dict:
        return payload

    return test_application


def test_request_within_size_limit_is_accepted() -> None:
    client = TestClient(build_test_app(body_limit=256))

    response = client.post(
        "/v1/test",
        json={"value": "synthetic"},
    )

    assert response.status_code == 200


def test_oversized_request_is_rejected() -> None:
    client = TestClient(build_test_app(body_limit=64))

    response = client.post(
        "/v1/test",
        json={"value": "x" * 200},
    )

    assert response.status_code == 413
    assert response.json()["detail"] == "Request body is too large"


def test_rate_limit_is_enforced() -> None:
    client = TestClient(build_test_app(rate_limit=2))

    first_response = client.post("/v1/test", json={"value": "one"})
    second_response = client.post("/v1/test", json={"value": "two"})
    third_response = client.post("/v1/test", json={"value": "three"})

    assert first_response.status_code == 200
    assert second_response.status_code == 200
    assert third_response.status_code == 429
    assert "Retry-After" in third_response.headers
