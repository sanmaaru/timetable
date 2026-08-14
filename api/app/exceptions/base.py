from starlette import status

from app.core.exceptions import ClientError


class ConflictError(ClientError):

    code = 'ALREADY_EXISTS'
    status_code = status.HTTP_409_CONFLICT


class NotFoundError(ClientError):

    code = 'NOT_FOUND'
    status_code = status.HTTP_404_NOT_FOUND
