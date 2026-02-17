import json
import time
import urllib
import urllib.parse
import uuid
from json import JSONDecodeError

import structlog
from fastapi.exceptions import RequestValidationError
from starlette import status
from starlette.types import ASGIApp, Scope, Receive, Send, Message

from app.util.logger import mask_sensitive_data

logger = structlog.get_logger()

MAX_BODY_SIZE = 1024 * 100
class RequestLogMiddleware:

    def __init__(self, app: ASGIApp, debug: bool = False):
        self.app = app
        self.debug = debug

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope['type'] != 'http':
            return await self.app(scope, receive, send)

        # === store context var ===
        request_id = None
        for header, value in scope.get('headers', []):
            if header == b"x-request-id":
                request_id = value.decode('latin1')
                break

        if not request_id:
            request_id = str(uuid.uuid4())

        client_ip = scope.get('client', ['unknown'])[0]

        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(
            request_id=request_id,
            method=scope['method'],
            url=str(scope['path']),
            client_ip=client_ip,
        )

        # === query json request ===
        request_body_chunk = []
        total_body_size = 0

        async def wrapped_receive() -> Message:
            nonlocal total_body_size
            message = await receive()

            if message['type'] == 'http.request':
                chunk = message.get('body', b"")
                if total_body_size < MAX_BODY_SIZE:
                    request_body_chunk.append(chunk)
                    total_body_size += len(chunk)

            return message

        # === logging ===
        start_time = time.perf_counter()
        response_status = status.HTTP_500_INTERNAL_SERVER_ERROR

        async def wrapped_send(message: Message) -> None:
            nonlocal response_status
            if message['type'] == 'http.response.start':
                response_status = message['status']

            await send(message)

        try:
            await self.app(scope, wrapped_receive, wrapped_send)
        except Exception as e:
            process_time = time.perf_counter() - start_time
            self._log_error(request_body_chunk, scope, response_status, process_time, e)
            # raise e
        else:
            process_time = time.perf_counter() - start_time
            if response_status >= 400:  # client error
                self._log_error(request_body_chunk, scope, response_status, process_time)
            else:
                logger.info('Request Handled', status_code=response_status, process_time=process_time)


    def _log_error(
        self,
        body_chunks: list,
        scope: Scope,
        status_code: int,
        processed_time: float,
        error: Exception = None,
    ):
        ## === read body ===
        body = b"".join(body_chunks)
        if len(body) > MAX_BODY_SIZE:
            body = body[:MAX_BODY_SIZE] + b"[TRUNCATED]"

        try:
            if body:
                body_json = json.loads(body)
                masked_body = mask_sensitive_data(body_json) if not self.debug else body_json
            else:
                masked_body = None
        except JSONDecodeError:
            masked_body = f'Cannot parse body JSON (len={len(body)})'

        ## === read header ===
        headers = {}
        for k, v in scope.get('headers', []):
            try:
                key = k.decode('latin1')
                value = v.decode('latin1')
                headers[key] = value
            except Exception:
                continue
        masked_header = mask_sensitive_data(headers) if not self.debug else headers

        ## === red query params ===
        query_params = {}
        query_bytes = scope.get('query_string', b"")
        if query_bytes:
            try:
                query_str = query_bytes.decode('latin1')
                parsed = urllib.parse.parse_qs(query_str)
                query_params = {k: v[0] if len(v) == 1 else v for k, v in parsed.items()}
            except Exception:
                query_params = {'error': 'parse_failed'}
        masked_query_params = mask_sensitive_data(query_params) if not self.debug else query_params

        log_payload = {
            'status_code': status_code,
            'processed_time': processed_time,
            'request': {
                'header': masked_header,
                'body': masked_body,
                'query_params': masked_query_params,
            }
        }

        if error:
            logger.error('Request failed with exception', exc_info=error, **log_payload)
        else:
            logger.warning('Request failed', **log_payload)