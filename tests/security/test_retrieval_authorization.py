"""Prove unauthorized records never enter retrieval results."""

from __future__ import annotations

import chromadb
import pytest

from app.core.auth import UserContext
from app.retrieval.service import RetrievalService


QUERY_TEXT = "zero trust architecture guidance"
TEST_EMBEDDING = [1.0, 0.0, 0.0]


@pytest.fixture
def retrieval_service(
    tmp_path,
    monkeypatch,
) -> RetrievalService:
    """
    Create an isolated Chroma collection containing one allowed record
    and four records that must be excluded.
    """

    client = chromadb.PersistentClient(
        path=str(tmp_path / "chroma"),
    )

    collection = client.create_collection(
        name="retrieval-authorization-test",
        embedding_function=None,
    )

    collection.add(
        ids=[
            "allowed-01",
            "wrong-tenant-01",
            "wrong-role-01",
            "too-sensitive-01",
            "unapproved-01",
        ],
        documents=[QUERY_TEXT] * 5,
        embeddings=[TEST_EMBEDDING] * 5,
        metadatas=[
            {
                "tenant": "portfolio-demo",
                "allowed_roles": ["security-architect"],
                "classification_rank": 1,
                "approved": True,
                "deleted": False,
                "source_id": "allowed-test-source",
                "page_or_section": "section 1",
                "source_version": "1.0",
            },
            {
                "tenant": "another-tenant",
                "allowed_roles": ["security-architect"],
                "classification_rank": 1,
                "approved": True,
                "deleted": False,
            },
            {
                "tenant": "portfolio-demo",
                "allowed_roles": ["viewer"],
                "classification_rank": 0,
                "approved": True,
                "deleted": False,
            },
            {
                "tenant": "portfolio-demo",
                "allowed_roles": ["security-architect"],
                "classification_rank": 2,
                "approved": True,
                "deleted": False,
            },
            {
                "tenant": "portfolio-demo",
                "allowed_roles": ["security-architect"],
                "classification_rank": 1,
                "approved": False,
                "deleted": False,
            },
        ],
    )

    def fake_embed(
        *,
        model: str,
        input: str,
    ) -> dict:
        """
        Return a fixed embedding so this test does not depend on Ollama.
        """

        assert model == "test-embedding-model"
        assert input == QUERY_TEXT

        return {
            "embeddings": [
                TEST_EMBEDDING,
            ]
        }

    monkeypatch.setattr(
        "app.retrieval.service.ollama.embed",
        fake_embed,
    )

    return RetrievalService(
        collection=collection,
        embedding_model="test-embedding-model",
        max_distance=1.0
    )


def test_search_excludes_unauthorized_records(
    retrieval_service: RetrievalService,
) -> None:
    context = UserContext(
        tenant="portfolio-demo",
        role="security-architect",
        clearance_rank=1,
    )

    results = retrieval_service.search(
        QUERY_TEXT,
        context,
        top_k=8,
    )

    ids = {
        item.chunk_id
        for item in results
    }

    assert "allowed-01" in ids
    assert "wrong-tenant-01" not in ids
    assert "wrong-role-01" not in ids
    assert "too-sensitive-01" not in ids
    assert "unapproved-01" not in ids