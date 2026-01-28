import atexit
import logging
import logging.handlers
import queue
import sys
from logging.handlers import QueueHandler
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

def mask_sensitive_data(data: Any, max_depth: int = 15, max_items=1000):
    if not isinstance(data, (dict, list)):
        return data

    if isinstance(data, dict):
        result = {}
    else:
        result = [None] * len(data)

    stack = [(data, result, 0)] # original, new, depth
    processed = 0

    while stack:
        src, dest, depth = stack.pop()

        if depth > max_depth:
            dest['...'] = "<Max Depth Exceeded>"
            continue

        processed += 1
        if processed > max_items:
            if isinstance(dest, dict):
                dest['...'] = "<Too Many Items>"
            return result

        if isinstance(src, dict):
            for k, v in src.items():
                if k.lower() in SENSITIVE_KEYS:
                    dest[k] = '*'
                elif isinstance(v, (dict, list)):
                    new_dest = {} if isinstance(v, dict) else [None] * len(v)
                    dest[k] = new_dest
                    stack.append((v, new_dest, depth + 1))
                else:
                    dest[k] = v

        elif isinstance(src, list):
            for i, v in enumerate(src):
                if isinstance(v, (dict, list)):
                    new_dest = {} if isinstance(v, dict) else [None] * len(v)
                    dest[i] = new_dest
                    stack.append((v, new_dest, depth + 1))
                else:
                    dest[i] = v

    return result

class NonBlockingQueueHandler(QueueHandler):
    def emit(self,record):
        try:
            record = self.prepare(record)
            self.queue.put_nowait(record)
        except queue.Full:
            sys.stderr.write("LOG DROPPED: Queue is full \n")



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
    log_queue = queue.Queue(maxsize=10000)
    queue_handler = NonBlockingQueueHandler(log_queue)

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
