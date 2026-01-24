import json
import time

import structlog
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import Message

from api.log.logger import mask_sensitive_data

logger = structlog.get_logger()

MAX_BODY_SIZE = 1024 * 100

class RequestLogMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # === store context var ===
        structlog.contextvars.clear_contextvars()

        request_id = request.headers.get('X-Request-Id', 'undefined')

        client_ip = request.headers.get('X-Forwarded-For')
        if not client_ip:
            client_ip = request.client.host if request.client else 'unknown'
        else:
            client_ip = client_ip.split(',')[0].strip()

        structlog.contextvars.bind_contextvars(
            request_id=request_id,
            method=request.method,
            url=str(request.url),
            client_ip=client_ip,
        )


        # === query json request ===
        content_length = int(request.headers.get('content-length', 0))
        if content_length > MAX_BODY_SIZE:
            logger.warning(
                "Too large body",
                content_length=content_length,
            )
            raise ValueError('Body is too large.')

        content_type = request.headers.get('content-type', '')

        if 'application/json' in content_type:
            try:
                body_bytes = await request.body()

                if body_bytes:
                    body_json = json.loads(body_bytes)
                    masked_body = mask_sensitive_data(body_json)
                    request.state.body = masked_body

                async def new_receive() -> Message:
                    return {'type': 'http.request', 'body': body_bytes}

                request._receive = new_receive

            except Exception as e:
                request.state.body = 'Body reade error'
                logger.error('Failed to read body', error=str(e))

        # === logging success log ===
        start_time = time.perf_counter()

        try:
            response = await call_next(request)

            process_time = time.perf_counter() - start_time

            await logger.info(
                "Request handled",
                status_code=response.status_code,
                process_time=process_time,
            )

            return response

        except Exception as e:
            raise e