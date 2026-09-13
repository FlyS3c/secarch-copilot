"""Tests for local model resource limits."""

import json
from types import SimpleNamespace

import pytest

from app.core.settings import settings
from app.workflows import architecture_review as workflow_module


def valid_model_response() -> str:
    return json.dumps(
        {
            "summary": "Synthetic review",
            "assumptions": [],
            "missing_information": [],
            "findings": [],
            "limitations": [],
        }
    )


def test_generation_uses_output_and_timeout_limits(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, object] = {}

    class FakeClient:
        def __init__(
            self,
            host: str,
            timeout: int,
        ) -> None:
            captured["host"] = host
            captured["timeout"] = timeout

        def chat(self, **kwargs: object) -> SimpleNamespace:
            captured["options"] = kwargs["options"]

            return SimpleNamespace(
                message=SimpleNamespace(
                    content=valid_model_response()
                )
            )

    monkeypatch.setattr(workflow_module, "Client", FakeClient)

    review = workflow_module.generate_review(
        prompt="Review this synthetic architecture.",
        ollama_host="http://127.0.0.1:11434",
    )

    assert review.summary == "Synthetic review"
    assert captured["timeout"] == settings.request_timeout_seconds
    assert captured["options"] == {
        "temperature": 0,
        "num_predict": settings.max_output_tokens,
    }


def test_busy_model_request_is_rejected(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class BusySemaphore:
        def acquire(self, blocking: bool = True) -> bool:
            assert blocking is False
            return False

        def release(self) -> None:
            raise AssertionError(
                "An unacquired semaphore must not be released"
            )

    monkeypatch.setattr(
        workflow_module,
        "_model_semaphore",
        BusySemaphore(),
    )

    with pytest.raises(
        workflow_module.ModelBusyError,
        match="already processing",
    ):
        workflow_module.generate_review(
            prompt="Review this synthetic architecture."
        )