"""Generate document and query embeddings with one named Ollama model."""

from __future__ import annotations

import math
from collections.abc import Sequence
from typing import Any

from ollama import Client


class OllamaEmbedder:
    def __init__(
        self,
        *,
        model: str = "embeddinggemma",
        host: str = "http://127.0.0.1:11434",
        batch_size: int = 32,
        client: Any | None = None,
    ) -> None:
        if batch_size < 1:
            raise ValueError("batch_size must be at least 1")
        self.model = model
        self.batch_size = batch_size
        self.client = client or Client(host=host)

    def embed_texts(self, texts: Sequence[str]) -> list[list[float]]:
        """Embed a non-empty sequence and verify output count and values."""
        if not texts:
            raise ValueError("No texts supplied for embedding")
        if any(not text.strip() for text in texts):
            raise ValueError("Empty text cannot be embedded")

        all_embeddings: list[list[float]] = []
        for start in range(0, len(texts), self.batch_size):
            batch = list(texts[start : start + self.batch_size])
            response = self.client.embed(
                model=self.model,
                input=batch,
                truncate=False,
            )
            embeddings = response["embeddings"]
            if len(embeddings) != len(batch):
                raise RuntimeError(
                    "Ollama returned a different number of embeddings than inputs"
                )
            all_embeddings.extend([list(vector) for vector in embeddings])

        if len(all_embeddings) != len(texts):
            raise RuntimeError("Final embedding count does not match text count")

        dimensions = {len(vector) for vector in all_embeddings}
        if len(dimensions) != 1 or 0 in dimensions:
            raise RuntimeError("Embedding vectors have inconsistent dimensions")
        if any(
            not math.isfinite(value) for vector in all_embeddings for value in vector
        ):
            raise RuntimeError("Embedding vectors contain non-finite values")
        return all_embeddings

    def embed_query(self, query: str) -> list[float]:
        return self.embed_texts([query])[0]
