"""Tests for trusted local authorization context."""

import pytest

from app.core.auth import build_local_context


def test_security_architect_context() -> None:
    context = build_local_context(
        "portfolio-demo",
        "security-architect",
    )

    assert context.tenant == "portfolio-demo"
    assert context.role == "security-architect"
    assert context.clearance_rank == 1


def test_viewer_receives_public_clearance() -> None:
    context = build_local_context(
        "portfolio-demo",
        "viewer",
    )

    assert context.clearance_rank == 0


def test_unknown_tenant_is_rejected() -> None:
    with pytest.raises(PermissionError, match="Unknown tenant or role"):
        build_local_context(
            "another-tenant",
            "security-architect",
        )


def test_unknown_role_is_rejected() -> None:
    with pytest.raises(PermissionError, match="Unknown tenant or role"):
        build_local_context(
            "portfolio-demo",
            "administrator",
        )