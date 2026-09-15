"""Structured response models for security architecture workflows."""

import re
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class Citation(BaseModel):
    """Reference to an exact retrieved document chunk."""

    model_config = ConfigDict(extra="forbid")

    source_id: str
    chunk_id: str
    page_or_section: str


class Finding(BaseModel):
    """One security architecture risk and recommendation."""

    model_config = ConfigDict(extra="forbid")

    finding_id: str
    risk: str
    severity: Literal["low", "medium", "high"]
    recommendation: str
    citations: list[Citation]
    human_review_required: bool = True

    @field_validator("finding_id")
    @classmethod
    def validate_finding_id(cls, value: str) -> str:
        cleaned = value.strip()

        if re.fullmatch(r"F-\d{3}", cleaned) is None:
            raise ValueError("finding_id must use the format F-001")

        return cleaned

    @field_validator("risk", "recommendation")
    @classmethod
    def validate_finding_text(cls, value: str) -> str:
        cleaned = value.strip()

        if not 20 <= len(cleaned) <= 1000:
            raise ValueError(
                "Risk and recommendation text must contain 20-1000 characters"
            )

        return cleaned

    @field_validator("citations")
    @classmethod
    def validate_citation_count(
        cls,
        value: list[Citation],
    ) -> list[Citation]:
        if not 1 <= len(value) <= 5:
            raise ValueError("A finding must contain 1-5 citations")

        return value

    @field_validator("human_review_required")
    @classmethod
    def require_human_review(cls, value: bool) -> bool:
        if value is not True:
            raise ValueError("human_review_required must be true")

        return value


class ArchitectureReview(BaseModel):
    """Validated response returned by the architecture-review workflow."""

    model_config = ConfigDict(extra="forbid")

    summary: str
    assumptions: list[str]
    missing_information: list[str]
    findings: list[Finding] = Field(max_length=10)
    limitations: list[str]


class Threat(BaseModel):
    """One STRIDE or AI-specific threat."""

    model_config = ConfigDict(extra="forbid")

    threat_id: str
    category: Literal[
        "spoofing",
        "tampering",
        "repudiation",
        "information-disclosure",
        "denial-of-service",
        "elevation-of-privilege",
        "prompt-injection",
        "data-and-model-poisoning",
        "vector-and-embedding-weakness",
        "model-or-adapter-compromise",
        "misinformation",
        "improper-output-handling",
        "unbounded-consumption",
    ]
    threat: str
    affected_assets: list[str]
    severity: Literal["low", "medium", "high"]
    mitigation: str
    residual_risk: str
    citations: list[Citation]
    human_review_required: bool = True


class ThreatModel(BaseModel):
    """Validated response returned by the threat-model workflow."""

    model_config = ConfigDict(extra="forbid")

    summary: str
    assumptions: list[str]
    missing_information: list[str]
    assets: list[str] = Field(max_length=30)
    trust_boundaries: list[str] = Field(max_length=30)
    threats: list[Threat] = Field(max_length=15)
    residual_risk_questions: list[str] = Field(max_length=20)
    limitations: list[str]
