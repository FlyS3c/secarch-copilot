"""Local FastAPI application for SecArch Copilot."""

from typing import Annotated
from uuid import uuid4

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

from app.api.dependencies import get_user_context
from app.api.limits import (
    LocalRateLimitMiddleware,
    RequestBodyLimitMiddleware,
)
from app.core.auth import UserContext
from app.core.settings import settings
from app.models.requests import (
    ArchitectureReviewRequest,
    ThreatModelRequest,
)
from app.models.responses import ArchitectureReview, ThreatModel
from app.workflows.architecture_review import (
    ModelBusyError,
    ModelTimeoutError,
    run_architecture_review,
)
from app.workflows.threat_model import run_threat_model

app = FastAPI(
    title="SecArch Copilot",
    docs_url="/docs",
)

app.add_middleware(
    LocalRateLimitMiddleware,
    max_requests=settings.rate_limit_requests,
    window_seconds=settings.rate_limit_window_seconds,
)

app.add_middleware(
    RequestBodyLimitMiddleware,
    max_body_bytes=settings.max_request_body_bytes,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500"],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "X-API-Key"],
)


@app.get("/health")
def health() -> dict[str, str]:
    """Return a minimal health response without sensitive details."""

    return {"status": "ok"}


@app.post(
    "/v1/architecture-review",
    response_model=ArchitectureReview,
)
def architecture_review(
    request: ArchitectureReviewRequest,
    context: Annotated[
        UserContext,
        Depends(get_user_context),
    ],
) -> ArchitectureReview:
    """Run an authenticated architecture review."""

    try:
        return run_architecture_review(
            request=request,
            context=context,
            request_id=str(uuid4()),
            audit_log_path=settings.audit_log_path,
        )
    except ModelBusyError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="The local model is busy. Try again shortly.",
            headers={"Retry-After": "2"},
        ) from exc
    except ModelTimeoutError as exc:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="The local model did not respond in time.",
        ) from exc


@app.post(
    "/v1/threat-model",
    response_model=ThreatModel,
)
def threat_model(
    request: ThreatModelRequest,
    context: Annotated[
        UserContext,
        Depends(get_user_context),
    ],
) -> ThreatModel:
    """Run an authenticated threat model."""

    try:
        return run_threat_model(
            request=request,
            context=context,
            request_id=str(uuid4()),
            audit_log_path=settings.audit_log_path,
        )
    except ModelBusyError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="The local model is busy. Try again shortly.",
            headers={"Retry-After": "2"},
        ) from exc
    except ModelTimeoutError as exc:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="The local model did not respond in time.",
        ) from exc