"""Create trusted authorization context for the local application."""

from dataclasses import dataclass

ALLOWED_TENANTS = {"portfolio-demo"}

ROLE_CLEARANCE = {
    "viewer": 0,
    "security-engineer": 1,
    "security-architect": 1,
}


@dataclass(frozen=True)
class UserContext:
    tenant: str
    role: str
    clearance_rank: int


def build_local_context(tenant: str, role: str) -> UserContext:
    """Build authorization context from trusted local configuration."""

    if tenant not in ALLOWED_TENANTS or role not in ROLE_CLEARANCE:
        raise PermissionError("Unknown tenant or role")

    return UserContext(
        tenant=tenant,
        role=role,
        clearance_rank=ROLE_CLEARANCE[role],
    )
