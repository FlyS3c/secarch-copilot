"""Verify architecture-review audit logging."""

import json
from uuid import uuid4

import pytest

from app.core.auth import UserContext
from app.models.requests import ArchitectureReviewRequest
from app.models.responses import (
    ArchitectureReview,
    Citation,
    Finding,
)
from app.retrieval.service import RetrievedChunk
from app.workflows import architecture_review as workflow_module


class FakeRetrievalService:
    def search(
        self,
        query: str,
        context: UserContext,
        top_k: int = 4,
    ) -> list[RetrievedChunk]:
        return [
            RetrievedChunk(
                chunk_id="synthetic-chunk-01",
                text="Approved synthetic security guidance.",
                metadata={},
                distance=0.25,
                source_id="synthetic-source",
                page_or_section="section 1",
                source_version="1",
            )
        ]


def test_review_writes_metadata_without_input(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    citation = Citation(
        source_id="synthetic-source",
        chunk_id="synthetic-chunk-01",
        page_or_section="section 1",
    )

    generated_review = ArchitectureReview(
        summary="Synthetic review",
        assumptions=[],
        missing_information=[],
        findings=[
            Finding(
                finding_id="F-01",
                risk="Synthetic risk",
                severity="medium",
                recommendation="Synthetic recommendation",
                citations=[citation],
                human_review_required=True,
            )
        ],
        limitations=[],
    )

    def fake_generate_review(**kwargs: object) -> ArchitectureReview:
        return generated_review

    monkeypatch.setattr(
        workflow_module,
        "generate_review",
        fake_generate_review,
    )

    request = ArchitectureReviewRequest(
        system_name="SYNTHETIC-CANARY-INPUT",
        purpose=(
            "Review a completely fictional architecture used only "
            "for an automated unit test."
        ),
        components=["Synthetic component"],
        data_classes=[],
        identities=[],
        integrations=[],
        network_boundaries=[],
    )

    log_path = tmp_path / "audit.jsonl"
    request_id = str(uuid4())

    result = workflow_module.run_architecture_review(
        request=request,
        context=UserContext(
            tenant="portfolio-demo",
            role="security-architect",
            clearance_rank=1,
        ),
        retrieval_service=FakeRetrievalService(),
        request_id=request_id,
        audit_log_path=log_path,
    )

    log_text = log_path.read_text(encoding="utf-8")
    saved_event = json.loads(log_text)

    assert result.summary == "Synthetic review"
    assert saved_event["request_id"] == request_id
    assert saved_event["result"] == "success"
    assert saved_event["source_ids"] == ["synthetic-source"]
    assert saved_event["retrieved_chunk_count"] == 1
    assert "SYNTHETIC-CANARY-INPUT" not in log_text
    assert "Approved synthetic security guidance" not in log_text