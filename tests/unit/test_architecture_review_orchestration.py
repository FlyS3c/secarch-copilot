"""Tests for architecture-review workflow orchestration."""

import pytest

from app.core.auth import build_local_context
from app.models.requests import ArchitectureReviewRequest
from app.models.responses import ArchitectureReview
from app.retrieval.service import RetrievedChunk
from app.workflows.architecture_review import (
    run_architecture_review,
)


class FakeRetrievalService:
    """Return predefined chunks without accessing Ollama or Chroma."""

    def __init__(self, chunks: list[RetrievedChunk]):
        self.chunks = chunks

    def search(self, query, context, top_k):
        return self.chunks


def synthetic_request() -> ArchitectureReviewRequest:
    return ArchitectureReviewRequest(
        system_name="Synthetic Portal",
        purpose=(
            "Provide fictional users with access to synthetic "
            "account information."
        ),
        components=["Web application", "API"],
        data_classes=["Synthetic data"],
        identities=["Customer", "Administrator"],
        integrations=["Synthetic identity provider"],
        network_boundaries=["Internet to application"],
    )


def retrieved_chunk() -> RetrievedChunk:
    return RetrievedChunk(
        chunk_id="chunk-001",
        text="Administrative access should use strong authentication.",
        metadata={
            "source_id": "nist-sp-800-53-rev5",
            "page_or_section": "page 341",
            "source_version": "Revision 5",
        },
        distance=0.50,
        source_id="nist-sp-800-53-rev5",
        page_or_section="page 341",
        source_version="Revision 5",
    )


def test_workflow_abstains_without_evidence(monkeypatch) -> None:
    def fail_if_called(*args, **kwargs):
        pytest.fail("Ollama must not be called without evidence")

    monkeypatch.setattr(
        "app.workflows.architecture_review.generate_review",
        fail_if_called,
    )

    review = run_architecture_review(
        request=synthetic_request(),
        context=build_local_context(
            "portfolio-demo",
            "security-architect",
        ),
        retrieval_service=FakeRetrievalService([]),
    )

    assert review.findings == []
    assert review.missing_information
    assert "Insufficient authorized evidence" in review.summary


def test_workflow_accepts_supported_citation(monkeypatch) -> None:
    def fake_generate_review(**kwargs):
        return ArchitectureReview.model_validate(
            {
                "summary": "Synthetic review completed.",
                "assumptions": [],
                "missing_information": [],
                "findings": [
                    {
                        "finding_id": "F-001",
                        "risk": "Administrative authentication is weak.",
                        "severity": "high",
                        "recommendation": (
                            "Require stronger administrative "
                            "authentication."
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
                "limitations": ["Human review is required."],
            }
        )

    monkeypatch.setattr(
        "app.workflows.architecture_review.generate_review",
        fake_generate_review,
    )

    review = run_architecture_review(
        request=synthetic_request(),
        context=build_local_context(
            "portfolio-demo",
            "security-architect",
        ),
        retrieval_service=FakeRetrievalService(
            [retrieved_chunk()]
        ),
    )

    assert len(review.findings) == 1
    assert review.findings[0].citations[0].chunk_id == "chunk-001"


def test_workflow_rejects_fabricated_citation(monkeypatch) -> None:
    def fake_generate_review(**kwargs):
        return ArchitectureReview.model_validate(
            {
                "summary": "Synthetic review completed.",
                "assumptions": [],
                "missing_information": [],
                "findings": [
                    {
                        "finding_id": "F-001",
                        "risk": "Synthetic risk.",
                        "severity": "medium",
                        "recommendation": "Synthetic recommendation.",
                        "citations": [
                            {
                                "source_id": "fabricated-source",
                                "chunk_id": "fabricated-chunk",
                                "page_or_section": "unknown",
                            }
                        ],
                        "human_review_required": True,
                    }
                ],
                "limitations": ["Human review is required."],
            }
        )

    monkeypatch.setattr(
        "app.workflows.architecture_review.generate_review",
        fake_generate_review,
    )

    with pytest.raises(
        ValueError,
        match="unsupported citation",
    ):
        run_architecture_review(
            request=synthetic_request(),
            context=build_local_context(
                "portfolio-demo",
                "security-architect",
            ),
            retrieval_service=FakeRetrievalService(
                [retrieved_chunk()]
            ),
        )