from starlette import status

from app.core.exceptions import ClientError


class AuthorizationError(ClientError):

    code = 'AUTHORIZATION_FAILED'
    status_code = status.HTTP_401_UNAUTHORIZED

class NoPermissionError(ClientError):

    code = 'NO_PERMISSION'
    status_code = status.HTTP_403_FORBIDDEN

class UnknownUserError(ClientError):

    code = 'UNKNOWN_USER'
    status_code = status.HTTP_404_NOT_FOUND


class RefreshTokenError(AuthorizationError):

    code = 'REFRESH_TOKEN_ERROR'
    status_code = status.HTTP_401_UNAUTHORIZED