"""Measure retrieval distances using relevant and irrelevant queries."""

from __future__ import annotations

import csv
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import chromadb
import yaml
from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parents[1]

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


from app.core.auth import build_local_context
from app.ingestion.embedder import OllamaEmbedder
from app.retrieval.service import build_authorization_filter


def required_environment_value(name: str) -> str:
    value = os.getenv(name)

    if not value:
        raise ValueError(f"Required environment variable is missing: {name}")

    return value


def main() -> int:
    load_dotenv(REPO_ROOT / ".env")

    data_root = (
        Path(required_environment_value("SECARCH_DATA_ROOT")).expanduser().resolve()
    )

    collection_name = required_environment_value("SECARCH_ACTIVE_COLLECTION")

    embedding_model = os.getenv(
        "EMBEDDING_MODEL",
        "embeddinggemma",
    )

    ollama_host = os.getenv(
        "OLLAMA_HOST",
        "http://127.0.0.1:11434",
    )

    tenant = os.getenv(
        "SECARCH_TENANT",
        "portfolio-demo",
    )

    role = os.getenv(
        "SECARCH_ROLE",
        "security-architect",
    )

    query_file = REPO_ROOT / "eval" / "retrieval-threshold-queries.yml"

    raw = yaml.safe_load(query_file.read_text(encoding="utf-8"))

    cases = raw.get("queries", [])

    if len(cases) < 20:
        raise ValueError("At least 20 calibration queries are required")

    context = build_local_context(
        tenant=tenant,
        role=role,
    )

    client = chromadb.PersistentClient(path=str(data_root / "chroma"))

    collection = client.get_collection(
        name=collection_name,
        embedding_function=None,
    )

    embedder = OllamaEmbedder(
        model=embedding_model,
        host=ollama_host,
    )

    rows: list[dict] = []

    for case in cases:
        query_id = str(case["id"])
        expected = str(case["expected"])
        query = str(case["query"])

        if expected not in {"relevant", "irrelevant"}:
            raise ValueError(f"{query_id}: expected must be relevant or irrelevant")

        embedding = embedder.embed_query(query)

        result = collection.query(
            query_embeddings=[embedding],
            n_results=4,
            where=build_authorization_filter(context),
            include=[
                "metadatas",
                "distances",
            ],
        )

        ids = result["ids"][0]
        metadatas = result["metadatas"][0]
        distances = result["distances"][0]

        if ids:
            best_chunk_id = str(ids[0])
            best_metadata = metadatas[0]
            best_distance = float(distances[0])

            source_id = str(best_metadata.get("source_id", ""))

            page_or_section = str(best_metadata.get("page_or_section", ""))
        else:
            best_chunk_id = ""
            source_id = ""
            page_or_section = ""
            best_distance = ""

        rows.append(
            {
                "query_id": query_id,
                "expected": expected,
                "query": query,
                "best_distance": best_distance,
                "source_id": source_id,
                "chunk_id": best_chunk_id,
                "page_or_section": page_or_section,
                "collection": collection_name,
                "embedding_model": embedding_model,
            }
        )

        print(
            f"{query_id:<10} {expected:<10} distance={best_distance} source={source_id}"
        )

    output_directory = REPO_ROOT / "eval" / "results"
    output_directory.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    output_file = output_directory / f"retrieval-threshold-{timestamp}.csv"

    with output_file.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=list(rows[0].keys()),
        )

        writer.writeheader()
        writer.writerows(rows)

    relevant_distances = [
        float(row["best_distance"])
        for row in rows
        if row["expected"] == "relevant" and row["best_distance"] != ""
    ]

    irrelevant_distances = [
        float(row["best_distance"])
        for row in rows
        if row["expected"] == "irrelevant" and row["best_distance"] != ""
    ]

    print()
    print(f"Results saved to: {output_file}")

    if relevant_distances and irrelevant_distances:
        largest_relevant = max(relevant_distances)
        smallest_irrelevant = min(irrelevant_distances)

        print(f"Largest relevant-query distance: {largest_relevant:.6f}")

        print(f"Smallest irrelevant-query distance: {smallest_irrelevant:.6f}")

        if largest_relevant < smallest_irrelevant:
            suggested_threshold = (largest_relevant + smallest_irrelevant) / 2

            print(f"Initial suggested threshold: {suggested_threshold:.6f}")
        else:
            print(
                "Relevant and irrelevant distances overlap. "
                "Review the CSV before selecting a threshold."
            )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
