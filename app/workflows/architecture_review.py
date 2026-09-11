"""Generate a structured enterprise security architecture review."""

from ollama import chat

from app.models.responses import ArchitectureReview


def generate_review(prompt: str) -> ArchitectureReview:
    """Call Ollama and validate its response against the required schema."""

    if not prompt.strip():
        raise ValueError("Prompt cannot be empty")

    response = chat(
        model="llama3.2:3b",
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        format=ArchitectureReview.model_json_schema(),
        options={
            "temperature": 0,
        },
    )

    if not response.message.content:
        raise ValueError("Ollama returned an empty response")

    return ArchitectureReview.model_validate_json(
        response.message.content
    )