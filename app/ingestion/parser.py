"""Extract text while retaining page or section provenance."""

from __future__ import annotations

import re
from pathlib import Path

from docx import Document
from pydantic import BaseModel, ConfigDict, Field
from pypdf import PdfReader


class ParsedSection(BaseModel):
    model_config = ConfigDict(extra="forbid")

    text: str = Field(min_length=1)
    location: str = Field(min_length=1)


def _normalize_text(text: str) -> str:
    text = text.replace("\x00", "")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _parse_pdf(path: Path) -> list[ParsedSection]:
    reader = PdfReader(path, strict=True)
    if reader.is_encrypted:
        raise ValueError(f"Password-protected PDFs are not supported: {path}")

    sections: list[ParsedSection] = []
    for page_number, page in enumerate(reader.pages, start=1):
        text = _normalize_text(page.extract_text() or "")
        if text:
            sections.append(ParsedSection(text=text, location=f"page {page_number}"))
    return sections


def _parse_docx(path: Path) -> list[ParsedSection]:
    document = Document(path)
    sections: list[ParsedSection] = []
    current_heading = "document start"
    current_paragraphs: list[str] = []

    def flush() -> None:
        text = _normalize_text("\n\n".join(current_paragraphs))
        if text:
            sections.append(ParsedSection(text=text, location=current_heading))
        current_paragraphs.clear()

    for paragraph in document.paragraphs:
        text = _normalize_text(paragraph.text)
        if not text:
            continue
        style_name = paragraph.style.name if paragraph.style is not None else ""
        if style_name.lower().startswith("heading"):
            flush()
            current_heading = text[:200]
        else:
            current_paragraphs.append(text)

    flush()
    return sections


def _parse_heading_text(path: Path, markdown: bool) -> list[ParsedSection]:
    raw = path.read_text(encoding="utf-8-sig", errors="strict")
    lines = raw.splitlines()
    sections: list[ParsedSection] = []
    current_heading = "document start"
    current_lines: list[str] = []

    def flush() -> None:
        text = _normalize_text("\n".join(current_lines))
        if text:
            sections.append(ParsedSection(text=text, location=current_heading))
        current_lines.clear()

    for line_number, line in enumerate(lines, start=1):
        heading_match = re.match(r"^\s{0,3}#{1,6}\s+(.+?)\s*#*\s*$", line)
        if markdown and heading_match:
            flush()
            current_heading = f"{heading_match.group(1)[:180]} (line {line_number})"
        else:
            current_lines.append(line)

    flush()
    return sections


def parse_document(path: Path, file_type: str) -> list[ParsedSection]:
    """Parse one supported document and require at least one text section."""
    try:
        if file_type == "pdf":
            sections = _parse_pdf(path)
        elif file_type == "docx":
            sections = _parse_docx(path)
        elif file_type == "markdown":
            sections = _parse_heading_text(path, markdown=True)
        elif file_type == "txt":
            sections = _parse_heading_text(path, markdown=False)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")
    except ValueError:
        raise
    except Exception as exc:
        raise ValueError(f"Failed to parse {path}: {exc}") from exc

    if not sections:
        raise ValueError(f"No extractable text found in {path}")
    return sections
