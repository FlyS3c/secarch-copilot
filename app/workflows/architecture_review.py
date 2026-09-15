"""Run the retrieval-augmented architecture-review workflow."""

import json
import logging
from datetime import UTC, datetime
from pathlib import Path
from threading import BoundedSemaphore
from time import perf_counter
from typing import Literal
from uuid import UUID, uuid4

import chromadb
import httpx
from ollama import Client, chat

from app.core.audit import AuditEvent, write_audit_event
from app.core.auth import UserContext
from app.core.chroma import build_chroma_settings
from app.core.settings import settings
from app.models.requests import ArchitectureReviewRequest
from app.models.responses import ArchitectureReview
from app.prompts.architecture_review import (
    build_architecture_review_prompt,
)
from app.retrieval.service import (
    RetrievalService,
    RetrievedChunk,
)

logger = logging.getLogger(__name__)


class ModelBusyError(RuntimeError):
    """Raised when the local model is already processing a request."""


class ModelTimeoutError(RuntimeError):
    """Raised when an Ollama operation exceeds its timeout."""


class CitationValidationError(ValueError):
    """Raised when generated citations fail validation."""


_model_semaphore = BoundedSemaphore(settings.max_concurrent_model_requests)


def generate_review(
    prompt: str,
    model: str = "llama3.2:3b",
    ollama_host: str | None = None,
) -> ArchitectureReview:
    if not prompt.strip():
        raise ValueError("Prompt cannot be empty")

    acquired = _model_semaphore.acquire(blocking=False)

    if not acquired:
        raise ModelBusyError("The local model is already processing a request")

    try:
        chat_function = (
            Client(
                host=ollama_host,
                timeout=settings.request_timeout_seconds,
            ).chat
            if ollama_host
            else chat
        )

        response = chat_function(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            format=ArchitectureReview.model_json_schema(),
            options={
                "temperature": 0,
                "num_predict": settings.max_output_tokens,
            },
        )
    except httpx.TimeoutException as exc:
        raise ModelTimeoutError("Ollama generation request timed out") from exc
    finally:
        _model_semaphore.release()

    if not response.message.content:
        raise ValueError("Ollama returned an empty response")

    return ArchitectureReview.model_validate_json(response.message.content)


def _format_values(label: str, values: list[str]) -> str:
    """Format one bounded request field for the system description."""

    cleaned_values = [value.strip() for value in values if value.strip()]

    formatted = "; ".join(cleaned_values) or "Not provided"

    return f"{label}: {formatted}"


def build_system_description(
    request: ArchitectureReviewRequest,
) -> str:
    """Convert validated request fields into a bounded description."""

    description = "\n".join(
        [
            f"System name: {request.system_name.strip()}",
            f"Purpose: {request.purpose.strip()}",
            _format_values("Components", request.components),
            _format_values("Data classes", request.data_classes),
            _format_values("Identities", request.identities),
            _format_values("Integrations", request.integrations),
            _format_values(
                "Network boundaries",
                request.network_boundaries,
            ),
        ]
    )

    if len(description) > settings.max_input_chars:
        raise ValueError(
            "Combined architecture description exceeds "
            f"{settings.max_input_chars} characters"
        )

    return description


def build_evidence_blocks(
    chunks: list[RetrievedChunk],
) -> list[str]:
    evidence_blocks: list[str] = []

    for evidence_number, chunk in enumerate(chunks, start=1):
        allowed_citation = json.dumps(
            {
                "source_id": chunk.source_id,
                "chunk_id": chunk.chunk_id,
                "page_or_section": chunk.page_or_section,
            },
            ensure_ascii=False,
        )

        evidence_blocks.append(
            f"EVIDENCE_{evidence_number}\n"
            f"ALLOWED_CITATION: {allowed_citation}\n"
            f"SOURCE_VERSION: {chunk.source_version}\n"
            f"DISTANCE: {chunk.distance:.6f}\n"
            "REFERENCE_TEXT:\n"
            f"{chunk.text}"
        )

    return evidence_blocks


def build_abstention_review() -> ArchitectureReview:
    """Return a safe response when no sufficient evidence is available."""

    return ArchitectureReview(
        summary=(
            "Insufficient authorized evidence was available to "
            "complete the architecture review."
        ),
        assumptions=[],
        missing_information=[
            ("Additional approved and relevant reference material is required.")
        ],
        findings=[],
        limitations=[
            (
                "No model-generated recommendations were produced "
                "because the evidence threshold was not met."
            )
        ],
    )


def validate_review_citations(
    review: ArchitectureReview,
    chunks: list[RetrievedChunk],
) -> None:
    """Reject missing or fabricated model citations."""

    allowed_citations = {
        (
            chunk.source_id,
            chunk.chunk_id,
            chunk.page_or_section,
        )
        for chunk in chunks
    }

    for finding in review.findings:
        if not finding.citations:
            raise CitationValidationError(
                f"Finding {finding.finding_id} has no citations"
            )

        for citation in finding.citations:
            citation_key = (
                citation.source_id,
                citation.chunk_id,
                citation.page_or_section,
            )

            if citation_key not in allowed_citations:
                raise CitationValidationError(
                    f"Finding {finding.finding_id} contains an unsupported citation"
                )


def _record_review_audit(
    request_id: UUID,
    context: UserContext,
    chunks: list[RetrievedChunk],
    started_at: float,
    result: Literal["success", "abstained", "error"],
    error_category: str | None,
    audit_log_path: Path,
) -> None:
    """Record metadata without recording prompts or document text."""

    event = AuditEvent(
        request_id=request_id,
        timestamp_utc=datetime.now(UTC),
        workflow="architecture_review",
        tenant=context.tenant,
        role=context.role,
        policy_decision="allowed",
        source_ids=sorted({chunk.source_id for chunk in chunks}),
        retrieved_chunk_count=len(chunks),
        latency_ms=int((perf_counter() - started_at) * 1000),
        result=result,
        error_category=error_category,
    )

    write_audit_event(event, audit_log_path)


def run_architecture_review(
    request: ArchitectureReviewRequest,
    context: UserContext,
    retrieval_service: RetrievalService | None = None,
    request_id: str | None = None,
    audit_log_path: Path | None = None,
) -> ArchitectureReview:
    started_at = perf_counter()
    audit_request_id = UUID(request_id) if request_id else uuid4()

    chunks: list[RetrievedChunk] = []
    audit_result: Literal[
        "success",
        "abstained",
        "error",
    ] = "error"
    error_category: str | None = "unhandled_error"

    try:
        description = build_system_description(request)

        if retrieval_service is None:
            chroma_client = chromadb.PersistentClient(
                path=str(settings.chroma_path),
                settings=build_chroma_settings(),
            )

            collection = chroma_client.get_collection(
                name=settings.secarch_active_collection,
                embedding_function=None,
            )

            retrieval_service = RetrievalService(
                collection=collection,
                embedding_model=settings.embedding_model,
                max_distance=settings.secarch_max_distance,
                ollama_host=settings.ollama_host,
                request_timeout_seconds=(settings.request_timeout_seconds),
            )
        try:
            purpose_chunks = retrieval_service.search(
                query=request.purpose.strip(),
                context=context,
                top_k=settings.max_results,
            )

            if purpose_chunks:
                chunks = retrieval_service.search(
                    query=description,
                    context=context,
                    top_k=settings.max_results,
                )
        except httpx.TimeoutException as exc:
            raise ModelTimeoutError("Ollama embedding request timed out") from exc

        if not chunks:
            audit_result = "abstained"
            error_category = None

            logger.info(
                "architecture_review_abstained tenant=%s role=%s",
                context.tenant,
                context.role,
            )

            return build_abstention_review()

        evidence_blocks = build_evidence_blocks(chunks)

        prompt = build_architecture_review_prompt(
            system_description=description,
            evidence_blocks=evidence_blocks,
        )

        review = generate_review(
            prompt=prompt,
            model=settings.generation_model,
            ollama_host=settings.ollama_host,
        )

        validate_review_citations(review, chunks)

        audit_result = "success"
        error_category = None

        logger.info(
            (
                "architecture_review_completed tenant=%s role=%s "
                "evidence_count=%d finding_count=%d"
            ),
            context.tenant,
            context.role,
            len(chunks),
            len(review.findings),
        )

        return review

    except ModelBusyError:
        error_category = "model_busy"
        raise
    except ModelTimeoutError:
        error_category = "model_timeout"
        raise
    except ValueError:
        error_category = "validation_error"
        raise
    finally:
        if audit_log_path is not None:
            try:
                _record_review_audit(
                    request_id=audit_request_id,
                    context=context,
                    chunks=chunks,
                    started_at=started_at,
                    result=audit_result,
                    error_category=error_category,
                    audit_log_path=audit_log_path,
                )
            except OSError:
                logger.exception(
                    "audit_event_write_failed request_id=%s",
                    audit_request_id,
                )
