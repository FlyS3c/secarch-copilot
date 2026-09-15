from __future__ import annotations

from pathlib import Path

import chromadb
import pytest

from app.core.chroma import build_chroma_settings
from app.ingestion.chunker import Chunk
from app.ingestion.indexer import create_index
from app.ingestion.manifest import SourceRecord


def approved_source() -> SourceRecord:
    return SourceRecord(
        source_id="synthetic-source",
        title="Synthetic Source",
        publisher="Glenn Merritt",
        version="1",
        official_url="https://example.com/source",
        retrieval_url="https://example.com/source.txt",
        license_name="Original synthetic material",
        retrieved_at="2026-09-08",
        local_relative_path="raw/synthetic/source.txt",
        file_type="txt",
        sha256="a" * 64,
        tenant="portfolio-demo",
        allowed_roles=["security-architect", "security-engineer"],
        classification="internal-demo",
        approved=True,
        approved_by="Glenn Merritt",
        approved_at="2026-09-08",
    )


def test_every_stored_record_has_access_metadata(tmp_path: Path) -> None:
    source = approved_source()
    chunks = [
        Chunk(
            chunk_id="synthetic-source-0001",
            source_id=source.source_id,
            text="Use phishing-resistant MFA.",
            location="Identity section",
            chunk_index=0,
        )
    ]

    count = create_index(
        chroma_path=tmp_path / "chroma",
        collection_name="secarch_test_2026_09_08_v1",
        embedding_model="test-embedding-model",
        sources_by_id={source.source_id: source},
        chunks=chunks,
        embeddings=[[0.1, 0.2, 0.3]],
    )

    assert count == 1
    client = chromadb.PersistentClient(
        path=str(tmp_path / "chroma"),
        settings=build_chroma_settings(),
    )
    record = client.get_collection("secarch_test_2026_09_08_v1").get()
    metadata = record["metadatas"][0]
    required = {
        "source_id",
        "chunk_id",
        "page_or_section",
        "tenant",
        "allowed_roles",
        "classification",
        "classification_rank",
        "approved",
        "source_version",
        "source_sha256",
        "ingested_at",
        "index_version",
        "deleted",
    }
    assert required <= set(metadata)
    assert metadata["approved"] is True


def test_existing_collection_is_not_overwritten(tmp_path: Path) -> None:
    chroma_path = tmp_path / "chroma"
    client = chromadb.PersistentClient(
        path=str(chroma_path),
        settings=build_chroma_settings(),
    )
    client.create_collection("secarch_test_existing_v1")

    source = approved_source()
    chunk = Chunk(
        chunk_id="synthetic-source-0001",
        source_id=source.source_id,
        text="Synthetic text.",
        location="section",
        chunk_index=0,
    )
    with pytest.raises(ValueError, match="already exists"):
        create_index(
            chroma_path=chroma_path,
            collection_name="secarch_test_existing_v1",
            embedding_model="test-model",
            sources_by_id={source.source_id: source},
            chunks=[chunk],
            embeddings=[[0.1, 0.2]],
        )
