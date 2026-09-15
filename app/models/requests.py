"""Validated request models for security-assistant workflows."""

from pydantic import BaseModel, ConfigDict, Field


class ArchitectureReviewRequest(BaseModel):
    """User-supplied description of an architecture to review."""

    model_config = ConfigDict(extra="forbid")

    system_name: str = Field(min_length=2, max_length=100)
    purpose: str = Field(min_length=20, max_length=2000)
    components: list[str] = Field(min_length=1, max_length=30)
    data_classes: list[str] = Field(
        default_factory=list,
        max_length=10,
    )
    identities: list[str] = Field(
        default_factory=list,
        max_length=20,
    )
    integrations: list[str] = Field(
        default_factory=list,
        max_length=20,
    )
    network_boundaries: list[str] = Field(
        default_factory=list,
        max_length=20,
    )


class ThreatModelRequest(ArchitectureReviewRequest):
    """Architecture description with additional data-flow information."""

    data_flows: list[str] = Field(
        default_factory=list,
        max_length=30,
    )
