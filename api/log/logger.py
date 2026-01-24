import atexit
import logging
import logging.handlers
import queue
import sys
from typing import Any

import structlog
from fastapi import Request

# TODO: 나중에 파일로 빼는거 고려
SENSITIVE_KEYS = {
    'password',
    'token',
    'access_token',
    'refresh_token',
    'authorization',
    'secret'
}

def mask_sensitive_data(data: Any):
    if isinstance(data, dict):
        return {k: '*' if k.lower() in SENSITIVE_KEYS else mask_sensitive_data(v)
                for k, v in data.items()}

    elif isinstance(data, list):
        return [mask_sensitive_data(v) for v in data]

    return data


def configure_logger(json: bool = True, level: str = 'INFO'):
    preprocessors = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.TimeStamper(fmt="iso"),
    ]

    if json:
        preprocessors = preprocessors + [
            structlog.processors.format_exc_info,
            structlog.processors.dict_tracebacks,
            structlog.processors.JSONRenderer(),
        ]
    else:
        preprocessors = preprocessors + [
            structlog.processors.format_exc_info,
            structlog.dev.ConsoleRenderer()
        ]

    structlog.configure(
        processors=preprocessors,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    formatter = structlog.stdlib.ProcessorFormatter(
        foreign_pre_chain=preprocessors,
        processors=[
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            structlog.processors.JSONRenderer() if json else structlog.dev.ConsoleRenderer()
        ]
    )
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    # use queue listener
    log_queue = queue.Queue(-1)
    queue_handler = logging.handlers.QueueHandler(log_queue)

    listener = logging.handlers.QueueListener(log_queue, handler)
    listener.start()

    atexit.register(listener.stop)

    root = logging.getLogger()
    root.handlers = [queue_handler]
    root.setLevel(level.upper())

    for _log in ['uvicorn', 'uvicorn.access', 'uvicorn.error']:
        logger = logging.getLogger(_log)
        logger.handlers = []
        logger.propagate = True


def _query_request_detail(request: Request, debug: bool = False):
    body = getattr(request.state, 'body', None)
    headers = dict(request.headers)
    if not debug:
        headers = mask_sensitive_data(headers)
    query = request.query_params

    return query, headers, body


async def log_request_detail(request: Request, message: str, debug: bool = False, level: str = 'info', **kwargs):
    logger = structlog.get_logger()

    query, headers, body = _query_request_detail(request, debug)

    log_method = getattr(logger, level)
    await log_method(
        message,
        request_detail={
            'query_params': query,
            'headers': headers,
            'body': body,
        },
        **kwargs
    )


async def log_exception_detail(request: Request, exc: Exception, debug: bool = False):
    logger = structlog.get_logger()

    query, headers, body = _query_request_detail(request, debug)

    await logger.exception(
        "Exception occurs when handling request!",
        error_message=str(exc),
        request_detail={
            'query_params': query,
            'headers': headers,
            'body': body,
        },
    )
