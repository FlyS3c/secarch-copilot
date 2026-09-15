"""Perform similarity searches only within authorized Chroma records."""

from dataclasses import dataclass
from typing import Any

import ollama
from chromadb.api.models.Collection import Collection

from app.core.auth import UserContext

MAX_RESULTS = 8

REQUIRED_CITATION_FIELDS = (
    "source_id",
    "page_or_section",
    "source_version",
)


@dataclass(frozen=True)
class RetrievedChunk:
    chunk_id: str
    text: str
    metadata: dict[str, Any]
    distance: float
    source_id: str
    page_or_section: str
    source_version: str

    @property
    def citation_label(self) -> str:
        return (
            f"{self.source_id} | "
            f"{self.page_or_section} | "
            f"{self.source_version} | "
            f"{self.chunk_id}"
        )


def build_authorization_filter(context: UserContext) -> dict:
    """Build the mandatory pre-retrieval authorization filter."""

    return {
        "$and": [
            {"tenant": {"$eq": context.tenant}},
            {"allowed_roles": {"$contains": context.role}},
            {
                "classification_rank": {
                    "$lte": context.clearance_rank,
                }
            },
            {"approved": {"$eq": True}},
            {"deleted": {"$eq": False}},
        ]
    }


class RetrievalService:
    def __init__(
        self,
        collection: Collection,
        embedding_model: str,
        max_distance: float,
        ollama_host: str | None = None,
        request_timeout_seconds: int = 90,
    ) -> None:
        if max_distance < 0:
            raise ValueError("max_distance cannot be negative")

        if request_timeout_seconds < 1:
            raise ValueError("request_timeout_seconds must be positive")

        self.collection = collection
        self.embedding_model = embedding_model
        self.max_distance = max_distance
        self.ollama_host = ollama_host
        self.request_timeout_seconds = request_timeout_seconds

    def search(
        self,
        query: str,
        context: UserContext,
        top_k: int = 4,
    ) -> list[RetrievedChunk]:
        if not query.strip():
            raise ValueError("Query cannot be empty")

        if not 1 <= top_k <= MAX_RESULTS:
            raise ValueError(f"top_k must be 1-{MAX_RESULTS}")

        embedding_client = (
            ollama.Client(
                host=self.ollama_host,
                timeout=self.request_timeout_seconds,
            )
            if self.ollama_host
            else ollama
        )

        embedding = embedding_client.embed(
            model=self.embedding_model,
            input=query,
        )["embeddings"][0]

        result = self.collection.query(
            query_embeddings=[embedding],
            n_results=top_k,
            where=build_authorization_filter(context),
            include=[
                "documents",
                "metadatas",
                "distances",
            ],
        )

        id_batches = result["ids"]
        document_batches = result.get("documents")
        metadata_batches = result.get("metadatas")
        distance_batches = result.get("distances")

        if (
            document_batches is None
            or metadata_batches is None
            or distance_batches is None
        ):
            raise ValueError("Chroma query returned incomplete retrieval results")

        if (
            not id_batches
            or not document_batches
            or not metadata_batches
            or not distance_batches
        ):
            return []

        chunk_ids = id_batches[0]
        documents = document_batches[0]
        metadatas = metadata_batches[0]
        distances = distance_batches[0]

        result_lengths = {
            len(chunk_ids),
            len(documents),
            len(metadatas),
            len(distances),
        }

        if len(result_lengths) != 1:
            raise ValueError("Chroma query returned inconsistent result lengths")

        chunks: list[RetrievedChunk] = []

        for chunk_id, text, metadata, distance in zip(
            chunk_ids,
            documents,
            metadatas,
            distances,
        ):
            distance_value = float(distance)

            # Lower Chroma distances indicate stronger matches.
            if distance_value > self.max_distance:
                continue

            if not isinstance(metadata, dict):
                raise TypeError(f"Chunk {chunk_id} has invalid metadata")

            missing_fields = [
                field for field in REQUIRED_CITATION_FIELDS if not metadata.get(field)
            ]

            if missing_fields:
                missing = ", ".join(missing_fields)
                raise ValueError(
                    f"Chunk {chunk_id} is missing citation metadata: {missing}"
                )

            if not isinstance(text, str) or not text.strip():
                raise ValueError(f"Chunk {chunk_id} has no usable text")

            chunks.append(
                RetrievedChunk(
                    chunk_id=chunk_id,
                    text=text,
                    metadata=metadata,
                    distance=distance_value,
                    source_id=str(metadata["source_id"]),
                    page_or_section=str(metadata["page_or_section"]),
                    source_version=str(metadata["source_version"]),
                )
            )

        # An empty list tells the workflow to abstain because it has
        # no evidence that meets the configured standard.
        return chunks
