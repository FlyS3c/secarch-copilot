"""API request-size and local rate-limit controls."""

from collections import defaultdict, deque
from math import ceil
from threading import Lock
from time import monotonic

from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Message, Receive, Scope, Send


class RequestBodyTooLarge(Exception):
    """Raised when an HTTP request exceeds the configured limit."""


class RequestBodyLimitMiddleware:
    """Reject oversized requests before FastAPI parses the JSON."""

    def __init__(
        self,
        app: ASGIApp,
        max_body_bytes: int,
    ) -> None:
        if max_body_bytes < 1:
            raise ValueError("max_body_bytes must be positive")

        self.app = app
        self.max_body_bytes = max_body_bytes

    async def __call__(
        self,
        scope: Scope,
        receive: Receive,
        send: Send,
    ) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        headers = dict(scope.get("headers", []))
        content_length = headers.get(b"content-length")

        if content_length is not None:
            try:
                declared_length = int(content_length)
            except ValueError:
                response = JSONResponse(
                    status_code=400,
                    content={"detail": "Invalid Content-Length header"},
                )
                await response(scope, receive, send)
                return

            if declared_length < 0:
                response = JSONResponse(
                    status_code=400,
                    content={"detail": "Invalid Content-Length header"},
                )
                await response(scope, receive, send)
                return

            if declared_length > self.max_body_bytes:
                response = JSONResponse(
                    status_code=413,
                    content={"detail": "Request body is too large"},
                )
                await response(scope, receive, send)
                return

        received_bytes = 0

        async def limited_receive() -> Message:
            nonlocal received_bytes

            message = await receive()

            if message["type"] == "http.request":
                received_bytes += len(message.get("body", b""))

                if received_bytes > self.max_body_bytes:
                    raise RequestBodyTooLarge

            return message

        try:
            await self.app(scope, limited_receive, send)
        except RequestBodyTooLarge:
            response = JSONResponse(
                status_code=413,
                content={"detail": "Request body is too large"},
            )
            await response(scope, receive, send)


class LocalRateLimitMiddleware:
    """Apply a small in-memory rate limit to versioned API routes."""

    def __init__(
        self,
        app: ASGIApp,
        max_requests: int,
        window_seconds: int,
    ) -> None:
        if max_requests < 1:
            raise ValueError("max_requests must be positive")

        if window_seconds < 1:
            raise ValueError("window_seconds must be positive")

        self.app = app
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._requests: dict[str, deque[float]] = defaultdict(deque)
        self._lock = Lock()

    async def __call__(
        self,
        scope: Scope,
        receive: Receive,
        send: Send,
    ) -> None:
        if (
            scope["type"] != "http"
            or scope.get("method") != "POST"
            or not scope.get("path", "").startswith("/v1/")
        ):
            await self.app(scope, receive, send)
            return

        client = scope.get("client")
        client_address = client[0] if client else "unknown"
        request_key = f"{client_address}:{scope['path']}"

        current_time = monotonic()
        cutoff = current_time - self.window_seconds

        with self._lock:
            timestamps = self._requests[request_key]

            while timestamps and timestamps[0] <= cutoff:
                timestamps.popleft()

            if len(timestamps) >= self.max_requests:
                retry_after = max(
                    1,
                    ceil(
                        timestamps[0]
                        + self.window_seconds
                        - current_time
                    ),
                )
            else:
                timestamps.append(current_time)
                retry_after = 0

        if retry_after:
            response = JSONResponse(
                status_code=429,
                content={"detail": "Rate limit exceeded"},
                headers={"Retry-After": str(retry_after)},
            )
            await response(scope, receive, send)
            return

        await self.app(scope, receive, send)