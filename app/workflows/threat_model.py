"""Run the retrieval-augmented threat-model workflow."""

import logging
from datetime import UTC, datetime
from pathlib import Path
from time import perf_counter
from typing import Literal
from uuid import UUID, uuid4

import chromadb
import httpx
from ollama import Client, chat

from app.core.audit import AuditEvent, write_audit_event
from app.core.auth import UserContext
from app.core.settings import settings
from app.models.requests import ThreatModelRequest
from app.models.responses import ThreatModel
from app.prompts.threat_model import build_threat_model_prompt
from app.retrieval.service import RetrievalService, RetrievedChunk
from app.workflows.architecture_review import (
    ModelBusyError,
    ModelTimeoutError,
    _model_semaphore,
    build_evidence_blocks,
    build_system_description,
)

logger = logging.getLogger(__name__)


def generate_threat_model(
    prompt: str,
    model: str = "llama3.2:3b",
    ollama_host: str | None = None,
) -> ThreatModel:
    """Generate and validate one structured threat model."""

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
            format=ThreatModel.model_json_schema(),
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

    return ThreatModel.model_validate_json(response.message.content)


def build_threat_model_description(
    request: ThreatModelRequest,
) -> str:
    """Build a bounded description that includes data flows."""

    description = build_system_description(request)

    cleaned_flows = [value.strip() for value in request.data_flows if value.strip()]

    formatted_flows = "; ".join(cleaned_flows) or "Not provided"

    description = f"{description}\nData flows: {formatted_flows}"

    if len(description) > settings.max_input_chars:
        raise ValueError(
            "Combined threat-model description exceeds "
            f"{settings.max_input_chars} characters"
        )

    return description


def build_abstention_threat_model() -> ThreatModel:
    """Return a safe result when evidence is insufficient."""

    return ThreatModel(
        summary=(
            "Insufficient authorized evidence was available to "
            "complete the threat model."
        ),
        assumptions=[],
        missing_information=[
            ("Additional approved and relevant reference material is required.")
        ],
        assets=[],
        trust_boundaries=[],
        threats=[],
        residual_risk_questions=[
            (
                "What additional approved reference material should "
                "be added before completing this threat model?"
            )
        ],
        limitations=[
            (
                "No model-generated threats were produced because "
                "the evidence threshold was not met."
            )
        ],
    )


def validate_threat_citations(
    threat_model: ThreatModel,
    chunks: list[RetrievedChunk],
) -> None:
    """Reject missing or fabricated threat citations."""

    allowed_citations = {
        (
            chunk.source_id,
            chunk.chunk_id,
            chunk.page_or_section,
        )
        for chunk in chunks
    }

    for threat in threat_model.threats:
        if not threat.citations:
            raise ValueError(f"Threat {threat.threat_id} has no citations")

        for citation in threat.citations:
            citation_key = (
                citation.source_id,
                citation.chunk_id,
                citation.page_or_section,
            )

            if citation_key not in allowed_citations:
                raise ValueError(
                    f"Threat {threat.threat_id} contains an unsupported citation"
                )


def _record_threat_model_audit(
    request_id: UUID,
    context: UserContext,
    chunks: list[RetrievedChunk],
    started_at: float,
    result: Literal["success", "abstained", "error"],
    error_category: str | None,
    audit_log_path: Path,
) -> None:
    """Record metadata without prompts or document text."""

    event = AuditEvent(
        request_id=request_id,
        timestamp_utc=datetime.now(UTC),
        workflow="threat_model",
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


def run_threat_model(
    request: ThreatModelRequest,
    context: UserContext,
    retrieval_service: RetrievalService | None = None,
    request_id: str | None = None,
    audit_log_path: Path | None = None,
) -> ThreatModel:
    """Run authorized retrieval and structured threat modeling."""

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
        description = build_threat_model_description(request)

        if retrieval_service is None:
            chroma_client = chromadb.PersistentClient(path=str(settings.chroma_path))

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
                "threat_model_abstained tenant=%s role=%s",
                context.tenant,
                context.role,
            )

            return build_abstention_threat_model()

        evidence_blocks = build_evidence_blocks(chunks)

        prompt = build_threat_model_prompt(
            system_description=description,
            evidence_blocks=evidence_blocks,
        )

        threat_model = generate_threat_model(
            prompt=prompt,
            model=settings.generation_model,
            ollama_host=settings.ollama_host,
        )

        validate_threat_citations(threat_model, chunks)

        audit_result = "success"
        error_category = None

        logger.info(
            (
                "threat_model_completed tenant=%s role=%s "
                "evidence_count=%d threat_count=%d"
            ),
            context.tenant,
            context.role,
            len(chunks),
            len(threat_model.threats),
        )

        return threat_model

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
                _record_threat_model_audit(
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
