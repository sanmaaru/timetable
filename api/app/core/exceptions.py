import structlog
from fastapi.exceptions import RequestValidationError
from starlette import status
from starlette.requests import Request
from starlette.responses import JSONResponse


class ClientError(Exception):

    code: str = 'BAD_REQUEST'
    status_code: int = status.HTTP_400_BAD_REQUEST

    def __init__(self, message: str, code: str = None, status_code: int = None, payload: dict = None):
        self.message = message
        self.code = code or self.code
        self.status_code = status_code or self.status_code
        self.payload = payload or {}

class ConflictError(ClientError):

    code = 'ALREADY_EXISTS'
    status_code = status.HTTP_409_CONFLICT


class BasicError(Exception):

    def __init__(self, message: str, **payloads):
        self.message = message
        self.payloads = payloads

    def __str__(self):
        payloads = []
        for k, v in self.payloads.items():
            payloads.append(f'{k}={v}')

        return f'[{', '.join(payloads)}] {self.message}'

    def __repr__(self):
        payloads = []
        for k, v in self.payloads.items():
            payloads.append(f'{k}={v}')

        return f'{self.__class__.__name__}(message={self.message}, {", ".join(payloads)})'


logger = structlog.get_logger()
async def handle_client_exception(request: Request, exc: ClientError):
    logger.warning(
        'Client Exception',
        code=exc.code,
        message=exc.message,
        payload=exc.payload,
        status_code=exc.status_code,
        path=str(request.url.path)
    )

    return JSONResponse(
        status_code=exc.status_code,
        content={
            'message': exc.message,
            'code': exc.code,
            **exc.payload,
        }
    )

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Handling pydantic validation errors
    """

    error_details = exc.errors()

    request.state.error = error_details
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content={
            'detail': error_details,
            'message': 'Invalid payload'
        }
    )

async def global_error_handler(request: Request, exc: Exception):
    request.state.error = exc
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            'message': "Internal Server Error",
            'request_id': request.headers.get('X-Request-Id')
        }
    )
