from app.ingestion.chunker import chunk_sections
from app.ingestion.parser import ParsedSection


def test_chunks_are_nonempty_bounded_and_keep_location() -> None:
    sections = [
        ParsedSection(
            text=("Security controls protect business outcomes. " * 40).strip(),
            location="Risk section",
        )
    ]

    chunks = chunk_sections(
        "synthetic-source",
        sections,
        max_chars=300,
        overlap_chars=30,
    )

    assert len(chunks) > 1
    assert all(chunk.text.strip() for chunk in chunks)
    assert all(len(chunk.text) <= 300 for chunk in chunks)
    assert all(chunk.location == "Risk section" for chunk in chunks)
    assert len({chunk.chunk_id for chunk in chunks}) == len(chunks)


def test_chunk_ids_are_deterministic() -> None:
    sections = [ParsedSection(text="A stable sentence.", location="page 1")]
    first = chunk_sections("source-one", sections)
    second = chunk_sections("source-one", sections)
    assert first[0].chunk_id == second[0].chunk_id
