from starlette import status

from app.core.exceptions import ClientError


class AuthorizationError(ClientError):

    code = 'AUTHORIZATION_FAILED'
    status_code = status.HTTP_401_UNAUTHORIZED


class NoPermissionError(ClientError):

    code = 'NO_PERMISSION'
    status_code = status.HTTP_403_FORBIDDEN
