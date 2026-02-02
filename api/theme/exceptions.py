from fastapi import FastAPI
from starlette import status
from starlette.requests import Request
from starlette.responses import JSONResponse
from ulid import ULID


class ThemeNotFoundException(Exception):

    def __init__(self, message: str = None, theme_id: ULID = None):
        self.message = message
        self.theme_id = theme_id

class ThemeNotOwnedByException(Exception):

    def __init__(self, message: str = None, theme_id: ULID = None):
        self.message = message
        self.theme_id = theme_id


# === handlers ===
async def theme_not_found_exception_handler(request: Request, exc: ThemeNotFoundException):
    request.state.error = exc
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={
            'message': exc.message,
            'invalid': exc.theme_id
        },
    )

async def theme_not_owned_by_exception_handler(request: Request, exc: ThemeNotOwnedByException):
    request.state.error = exc
    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content={
            'message': exc.message,
            'invalid': exc.theme_id
        },
    )

def include_exception_handlers(app: FastAPI):
    app.add_exception_handler(ThemeNotFoundException, theme_not_found_exception_handler)
    app.add_exception_handler(ThemeNotOwnedByException, theme_not_owned_by_exception_handler)
