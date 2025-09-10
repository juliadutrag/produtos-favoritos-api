import time
import uuid

import structlog
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

logger = structlog.get_logger(__name__)

class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        structlog.contextvars.clear_contextvars()
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        structlog.contextvars.bind_contextvars(request_id=request_id)

        start_time = time.monotonic()
        logger.info(
            "Requisição recebida",
            http_method=request.method,
            http_path=request.url.path,
            client_ip=request.client.host if request.client else "unknown",
        )

        response = await call_next(request)

        process_time = (time.monotonic() - start_time) * 1000
        logger.info(
            "Resposta enviada",
            http_status_code=response.status_code,
            duration_ms=round(process_time, 2),
        )

        response.headers["X-Request-ID"] = request_id
        return response
