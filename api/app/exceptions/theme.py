from starlette import status

from app.core.exceptions import ClientError


class ThemeNotOwnedByError(ClientError):

    code = 'THEME_NOT_OWNED'
    status_code = status.HTTP_403_FORBIDDEN

class LastThemeDeleteError(ClientError):

    code = 'LAST_THEME_DELETE'
    status_code = status.HTTP_409_CONFLICT

class ThemeInUseError(ClientError):

    code = 'THEME_IN_USE'
    staus = status.HTTP_409_CONFLICT