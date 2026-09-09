"""Split parsed sections into deterministic, bounded chunks."""

from __future__ import annotations

import hashlib
import re

from pydantic import BaseModel, ConfigDict, Field

from app.ingestion.parser import ParsedSection


class Chunk(BaseModel):
    model_config = ConfigDict(extra="forbid")

    chunk_id: str = Field(min_length=1)
    source_id: str = Field(min_length=1)
    text: str = Field(min_length=1)
    location: str = Field(min_length=1)
    chunk_index: int = Field(ge=0)


def _split_long_text(text: str, max_chars: int) -> list[str]:
    sentences = re.split(r"(?<=[.!?])\s+|\n{2,}", text)
    pieces: list[str] = []

    for sentence in sentences:
        sentence = sentence.strip()
        while len(sentence) > max_chars:
            split_at = sentence.rfind(" ", 0, max_chars + 1)
            if split_at < max_chars // 2:
                split_at = max_chars
            pieces.append(sentence[:split_at].strip())
            sentence = sentence[split_at:].strip()
        if sentence:
            pieces.append(sentence)

    return pieces


def chunk_sections(
    source_id: str,
    sections: list[ParsedSection],
    *,
    max_chars: int = 3_000,
    overlap_chars: int = 300,
) -> list[Chunk]:
    """Chunk by logical section, then bounded character length with overlap."""
    if max_chars < 200:
        raise ValueError("max_chars must be at least 200")
    if overlap_chars < 0 or overlap_chars >= max_chars:
        raise ValueError("overlap_chars must be >= 0 and smaller than max_chars")

    chunks: list[Chunk] = []
    chunk_index = 0

    for section in sections:
        pieces = _split_long_text(section.text, max_chars)
        current = ""

        for piece in pieces:
            candidate = f"{current} {piece}".strip()
            if current and len(candidate) > max_chars:
                chunk_text = current.strip()
                identifier = hashlib.sha256(
                    f"{source_id}|{section.location}|{chunk_index}|{chunk_text}".encode(
                        "utf-8"
                    )
                ).hexdigest()[:16]
                chunks.append(
                    Chunk(
                        chunk_id=f"{source_id}-{identifier}",
                        source_id=source_id,
                        text=chunk_text,
                        location=section.location,
                        chunk_index=chunk_index,
                    )
                )
                chunk_index += 1
                overlap = chunk_text[-overlap_chars:] if overlap_chars else ""
                current = f"{overlap} {piece}".strip()
                if len(current) > max_chars:
                    current = piece
            else:
                current = candidate

        if current.strip():
            chunk_text = current.strip()
            identifier = hashlib.sha256(
                f"{source_id}|{section.location}|{chunk_index}|{chunk_text}".encode(
                    "utf-8"
                )
            ).hexdigest()[:16]
            chunks.append(
                Chunk(
                    chunk_id=f"{source_id}-{identifier}",
                    source_id=source_id,
                    text=chunk_text,
                    location=section.location,
                    chunk_index=chunk_index,
                )
            )
            chunk_index += 1

    if not chunks:
        raise ValueError(f"No chunks produced for {source_id}")
    if any(not chunk.text.strip() or len(chunk.text) > max_chars for chunk in chunks):
        raise ValueError("Chunking produced an empty or oversized chunk")
    return chunks
