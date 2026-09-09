"""Write approved chunks and their supplied embeddings to a new Chroma index."""

from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import chromadb

from app.ingestion.chunker import Chunk
from app.ingestion.manifest import SourceRecord


COLLECTION_NAME_PATTERN = re.compile(r"^[a-z0-9][a-z0-9._-]{1,510}[a-z0-9]$")


def build_metadata(
    source: SourceRecord,
    chunk: Chunk,
    *,
    ingestion_time: str,
    index_version: str,
) -> dict[str, Any]:
    if not source.approved:
        raise ValueError(f"Cannot index unapproved source: {source.source_id}")

    return {
        "source_id": source.source_id,
        "chunk_id": chunk.chunk_id,
        "page_or_section": chunk.location,
        "tenant": source.tenant,
        "allowed_roles": list(source.allowed_roles),
        "classification": source.classification,
        "classification_rank": source.classification_rank,
        "approved": source.approved,
        "source_version": source.version,
        "source_sha256": source.sha256,
        "ingested_at": ingestion_time,
        "index_version": index_version,
        "deleted": False,
    }


def create_index(
    *,
    chroma_path: Path,
    collection_name: str,
    embedding_model: str,
    sources_by_id: dict[str, SourceRecord],
    chunks: list[Chunk],
    embeddings: list[list[float]],
    batch_size: int = 100,
) -> int:
    """Create a brand-new collection; never overwrite an existing collection."""
    if not COLLECTION_NAME_PATTERN.fullmatch(collection_name):
        raise ValueError(f"Invalid Chroma collection name: {collection_name}")
    if not chunks:
        raise ValueError("No chunks supplied to the indexer")
    if len(chunks) != len(embeddings):
        raise ValueError("Chunk count and embedding count do not match")
    if len({chunk.chunk_id for chunk in chunks}) != len(chunks):
        raise ValueError("Duplicate chunk IDs detected")

    chroma_path.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=str(chroma_path))
    existing_names = {collection.name for collection in client.list_collections()}
    if collection_name in existing_names:
        raise ValueError(
            f"Collection already exists; choose a new version: {collection_name}"
        )

    ingestion_time = datetime.now(timezone.utc).isoformat()
    collection = client.create_collection(
        name=collection_name,
        embedding_function=None,
        metadata={
            "embedding_model": embedding_model,
            "index_version": collection_name,
            "created_at": ingestion_time,
        },
    )

    try:
        for start in range(0, len(chunks), batch_size):
            chunk_batch = chunks[start : start + batch_size]
            embedding_batch = embeddings[start : start + batch_size]
            metadatas: list[dict[str, Any]] = []
            for chunk in chunk_batch:
                try:
                    source = sources_by_id[chunk.source_id]
                except KeyError as exc:
                    raise ValueError(
                        f"No manifest source found for chunk {chunk.chunk_id}"
                    ) from exc
                metadatas.append(
                    build_metadata(
                        source,
                        chunk,
                        ingestion_time=ingestion_time,
                        index_version=collection_name,
                    )
                )
            collection.add(
                ids=[chunk.chunk_id for chunk in chunk_batch],
                documents=[chunk.text for chunk in chunk_batch],
                embeddings=embedding_batch,
                metadatas=metadatas,
            )

        stored_count = collection.count()
        if stored_count != len(chunks):
            raise RuntimeError(
                f"Chroma stored {stored_count} records; expected {len(chunks)}"
            )
    except Exception:
        # This collection was created by this function and is not active yet.
        # Remove a partial build so the same failed version is never promoted.
        client.delete_collection(name=collection_name)
        raise
    return stored_count
