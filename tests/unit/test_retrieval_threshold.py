"""Test citation handling and weak-evidence rejection."""

from app.core.auth import UserContext
from app.retrieval.service import RetrievalService

TEST_EMBEDDING = [1.0, 0.0, 0.0]


class FakeCollection:
    def query(self, **kwargs) -> dict:
        return {
            "ids": [
                [
                    "relevant-01",
                    "weak-01",
                ]
            ],
            "documents": [
                [
                    "Use phishing-resistant MFA.",
                    "Unrelated weak evidence.",
                ]
            ],
            "metadatas": [
                [
                    {
                        "source_id": "test-standard",
                        "page_or_section": "Identity section",
                        "source_version": "1.0",
                    },
                    {
                        "source_id": "test-standard",
                        "page_or_section": "Unrelated section",
                        "source_version": "1.0",
                    },
                ]
            ],
            "distances": [
                [
                    0.20,
                    1.50,
                ]
            ],
        }


def fake_embed(*, model: str, input: str) -> dict:
    return {
        "embeddings": [
            TEST_EMBEDDING,
        ]
    }


def test_weak_evidence_is_excluded(
    monkeypatch,
) -> None:
    monkeypatch.setattr(
        "app.retrieval.service.ollama.embed",
        fake_embed,
    )

    service = RetrievalService(
        collection=FakeCollection(),
        embedding_model="test-model",
        max_distance=0.50,
    )

    context = UserContext(
        tenant="portfolio-demo",
        role="security-architect",
        clearance_rank=1,
    )

    results = service.search(
        "How should authentication be secured?",
        context,
    )

    assert len(results) == 1
    assert results[0].chunk_id == "relevant-01"
    assert results[0].source_id == "test-standard"
    assert results[0].page_or_section == "Identity section"
    assert results[0].source_version == "1.0"
    assert "relevant-01" in results[0].citation_label


def test_no_acceptable_evidence_returns_empty_list(
    monkeypatch,
) -> None:
    monkeypatch.setattr(
        "app.retrieval.service.ollama.embed",
        fake_embed,
    )

    service = RetrievalService(
        collection=FakeCollection(),
        embedding_model="test-model",
        max_distance=0.10,
    )

    context = UserContext(
        tenant="portfolio-demo",
        role="security-architect",
        clearance_rank=1,
    )

    results = service.search(
        "How should authentication be secured?",
        context,
    )

    assert results == []
