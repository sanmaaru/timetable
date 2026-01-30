import asyncio
import json
import time
import uuid

import structlog
from fastapi import Request
from starlette.concurrency import run_in_threadpool
from starlette.background import BackgroundTask, BackgroundTasks
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from log.logger import mask_sensitive_data

logger = structlog.get_logger()

MAX_BODY_SIZE = 1024 * 100

class RequestLogMiddleware(BaseHTTPMiddleware):

    def __init__(self, app: ASGIApp, debug: bool = False):
        super().__init__(app)
        self.debug = debug

    async def dispatch(self, request: Request, call_next):
        # === store context var ===
        structlog.contextvars.clear_contextvars()

        request_id = request.headers.get('X-Request-Id')
        if not request_id:
            request_id = str(uuid.uuid4())

        client_ip = request.client.host if request.client else 'unknown'

        structlog.contextvars.bind_contextvars(
            request_id=request_id,
            method=request.method,
            url=str(request.url),
            client_ip=client_ip,
        )


        # === query json request ===
        content_length = int(request.headers.get('content-length', 0))
        content_type = request.headers.get('content-type', '')

        should_cache = (
            content_length <= MAX_BODY_SIZE and
            'application/json' in content_type
        )

        if should_cache:
            await request.body()

        # === logging ===
        start_time = time.perf_counter()

        try:
            response = await call_next(request)

            process_time = time.perf_counter() - start_time

            if response.status_code >= 400:
                current_context = structlog.contextvars.get_contextvars()
                error = getattr(request.state, 'error', None)
                method = 'error' if response.status_code >= 500 else 'info'

                body_bytes = b""
                if should_cache:
                    body_bytes = await request.body()

                header = dict(request.headers)
                query_params = dict(request.query_params)

                task_args = {
                    'body_bytes': body_bytes,
                    'header': header,
                    'query_params': query_params,
                    'status_code': response.status_code,
                    'log_method': method,
                    'is_cached': should_cache,
                    'error': error,
                    'context_vars': current_context,
                    'process_time': process_time,
                }

                if response.background is None:
                    response.background = BackgroundTask(self._log_error, **task_args)

                elif isinstance(response.background, BackgroundTasks):
                    response.background.add_task(self._log_error, **task_args)

                elif isinstance(response.background, BackgroundTask):
                    existing_task = response.background
                    new_task = BackgroundTasks()

                    new_task.tasks.append(existing_task)
                    new_task.add_task(self._log_error, **task_args)
                    response.background = new_task

            else:
                await logger.info(
                    'Request handled',
                    status_code=response.status_code,
                    process_time=process_time
                )

            return response

        except Exception as e:
            current_context = structlog.contextvars.get_contextvars()
            error = e
            method = 'error'

            body_bytes = b""
            if should_cache:
                body_bytes = await request.body()

            header = dict(request.headers)
            query_params = dict(request.query_params)

            task_args = {
                'body_bytes': body_bytes,
                'header': header,
                'query_params': query_params,
                'status_code': 500,
                'log_method': method,
                'is_cached': should_cache,
                'error': error,
                'context_vars': current_context,
            }

            asyncio.create_task(
                self._log_error(**task_args),
            )

            raise e

    async def _log_error(
            self,
            body_bytes: bytes,
            header: dict,
            query_params: dict,
            status_code: int,
            log_method: str,
            is_cached: bool,
            error = None,
            context_vars: dict = None,
            process_time = None
    ):
        if context_vars:
            structlog.contextvars.clear_contextvars()
            structlog.contextvars.bind_contextvars(**context_vars)

        masked_header, masked_body = await run_in_threadpool(
            self._parse_request,
            body_bytes=body_bytes,
            header=header,
            is_cached=is_cached
        )

        log_data = {
            'status_code': status_code,
            'request': {
                'header': masked_header,
                'body': masked_body,
                'query_params': query_params,
            }
        }

        if error:
            log_data['error'] = error

        if process_time:
            log_data['process_time'] = process_time

        method = getattr(logger, log_method.lower())


        method(
            'Request failed',
            **log_data,
        )

    def _parse_request(self, body_bytes, header, is_cached):
        if is_cached and body_bytes:
            try:
                body_json = json.loads(body_bytes)
                masked_body = mask_sensitive_data(body_json) if not self.debug else body_json
            except json.JSONDecodeError:
                masked_body = 'Cannot parse body: Invalid JSON'
            except Exception:
                masked_body = 'Cannot parse body'
        else:
            masked_body = 'Body skipped' if not is_cached else 'Body is not cached'


        masked_header = mask_sensitive_data(header) if not self.debug else header
        return masked_header, masked_body

