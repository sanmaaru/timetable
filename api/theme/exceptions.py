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

class LastThemeDeleteException(Exception):
    def __init__(self, message: str = None):
        self.message = message

class ThemeInUseException(Exception):
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

async def last_theme_delete_exception_handler(request: Request, exc: LastThemeDeleteException):
    request.state.error = exc
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content={
            'message': exc.message,
        }
    )

async def theme_in_use_exception_handler(request: Request, exc: ThemeInUseException):
    request.state.error = exc
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content={
            'message': exc.message,
        }
    )

def include_exception_handlers(app: FastAPI):
    app.add_exception_handler(ThemeNotFoundException, theme_not_found_exception_handler)
    app.add_exception_handler(ThemeNotOwnedByException, theme_not_owned_by_exception_handler)
    app.add_exception_handler(LastThemeDeleteException, last_theme_delete_exception_handler)
    app.add_exception_handler(ThemeInUseException, theme_in_use_exception_handler)
