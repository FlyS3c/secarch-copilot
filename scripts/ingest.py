"""Run the secure ingestion pipeline from manifest through versioned Chroma."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from dotenv import load_dotenv


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from app.ingestion.chunker import Chunk, chunk_sections
from app.ingestion.embedder import OllamaEmbedder
from app.ingestion.indexer import create_index
from app.ingestion.manifest import SourceRecord, load_manifest
from app.ingestion.parser import parse_document
from app.ingestion.validators import (
    SourceValidationError,
    validate_extracted_text,
    validate_manifest_uniqueness,
    validate_source_file,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--collection")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--max-file-mb", type=int, default=25)
    return parser.parse_args()


def required_env_path(name: str) -> Path:
    value = os.getenv(name)
    if not value:
        raise ValueError(f"Required environment variable is missing: {name}")
    return Path(value).expanduser().resolve()


def main() -> int:
    load_dotenv(REPO_ROOT / ".env")
    args = parse_args()

    if not args.dry_run and not args.collection:
        print("ERROR: --collection is required unless --dry-run is used")
        return 2

    try:
        data_root = required_env_path("SECARCH_DATA_ROOT")
        manifest_path = (
            args.manifest
            if args.manifest.is_absolute()
            else (REPO_ROOT / args.manifest).resolve()
        )
        manifest = load_manifest(manifest_path)
        validate_manifest_uniqueness(manifest)
    except Exception as exc:
        print(f"ERROR: {exc}")
        return 1

    accepted_sources: dict[str, SourceRecord] = {}
    all_chunks: list[Chunk] = []
    blocking_errors: list[str] = []

    for source in manifest.sources:
        if not source.approved:
            print(f"SKIPPED unapproved source: {source.source_id}")
            continue

        try:
            validation = validate_source_file(
                source,
                data_root,
                max_file_bytes=args.max_file_mb * 1024 * 1024,
            )
            sections = parse_document(validation.path, source.file_type)
            full_text = "\n\n".join(section.text for section in sections)
            warnings = validate_extracted_text(full_text)
            chunks = chunk_sections(source.source_id, sections)
        except (OSError, ValueError, SourceValidationError) as exc:
            blocking_errors.append(f"{source.source_id}: {exc}")
            continue

        accepted_sources[source.source_id] = source
        all_chunks.extend(chunks)
        print(
            f"VALID {source.source_id}: "
            f"{len(sections)} section(s), {len(chunks)} chunk(s)"
        )
        for warning in warnings:
            print(f"  WARNING: {warning}")

    if blocking_errors:
        print("\nINGESTION ABORTED. Approved sources failed validation:")
        for error in blocking_errors:
            print(f"- {error}")
        print("No embeddings or Chroma records were created.")
        return 1

    if not all_chunks:
        print("ERROR: No approved chunks are available for ingestion")
        return 1

    if args.dry_run:
        print(
            f"\nDRY RUN PASSED: {len(accepted_sources)} source(s), "
            f"{len(all_chunks)} chunk(s), no database writes"
        )
        return 0

    embedding_model = os.getenv("EMBEDDING_MODEL", "embeddinggemma")
    ollama_host = os.getenv("OLLAMA_HOST", "http://127.0.0.1:11434")
    embedder = OllamaEmbedder(model=embedding_model, host=ollama_host)

    try:
        embeddings = embedder.embed_texts([chunk.text for chunk in all_chunks])
        stored_count = create_index(
            chroma_path=data_root / "chroma",
            collection_name=args.collection,
            embedding_model=embedding_model,
            sources_by_id=accepted_sources,
            chunks=all_chunks,
            embeddings=embeddings,
        )
    except Exception as exc:
        print(f"ERROR: Index creation failed: {exc}")
        return 1

    print(
        f"\nINGESTION COMPLETE: {stored_count} records stored in "
        f"{args.collection}"
    )
    print("Test this collection before changing the configured active collection.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
