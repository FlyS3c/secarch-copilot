"""Security-focused configuration for the embedded Chroma client."""

from chromadb.config import Settings as ChromaSettings


def build_chroma_settings() -> ChromaSettings:
    """Disable Chroma product telemetry for the local application."""

    return ChromaSettings(anonymized_telemetry=False)
