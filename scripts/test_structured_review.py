"""Run one synthetic structured-output test against local Ollama."""

import sys
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]

if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))

from app.prompts.architecture_review import (
    build_architecture_review_prompt,
)
from app.workflows.architecture_review import generate_review


def main() -> None:
    """Generate and display one synthetic architecture review."""

    prompt = build_architecture_review_prompt(
        system_description=(
            "A fictional company stores public marketing files in "
            "Azure Blob Storage. Administrators use passwords without "
            "multifactor authentication. The storage account is "
            "accessible from the internet."
        ),
        evidence_blocks=[
            (
                "SOURCE_ID: nist-sp-800-53-rev5\n"
                "CHUNK_ID: synthetic-chunk-001\n"
                "PAGE_OR_SECTION: page 341\n"
                "TEXT: Authentication controls should be selected "
                "according to organizational risk."
            )
        ],
    )

    review = generate_review(prompt)

    print(review.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
