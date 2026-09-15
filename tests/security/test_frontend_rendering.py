"""Verify untrusted output cannot be rendered as executable HTML."""

from pathlib import Path

APP_JS_PATH = Path(__file__).resolve().parents[2] / "frontend" / "app.js"


def test_frontend_uses_text_only_dom_rendering() -> None:
    app_js = APP_JS_PATH.read_text(encoding="utf-8")

    assert ".textContent" in app_js

    forbidden_patterns = (
        ".innerHTML",
        ".outerHTML",
        "insertAdjacentHTML",
        "document.write",
        "eval(",
    )

    for pattern in forbidden_patterns:
        assert pattern not in app_js
