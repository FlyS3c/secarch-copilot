"""Authentication and authorization dependencies for the local API."""

import secrets
from typing import Annotated

from fastapi import Header, HTTPException, status

from app.core.auth import UserContext, build_local_context
from app.core.settings import settings


def get_user_context(
    x_api_key: Annotated[
        str | None,
        Header(alias="X-API-Key"),
    ] = None,
) -> UserContext:
    """Authenticate the request and return trusted authorization context."""

    if x_api_key is None or not secrets.compare_digest(
        x_api_key,
        settings.secarch_local_api_key,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    return build_local_context(
        settings.secarch_tenant,
        settings.secarch_role,
    )