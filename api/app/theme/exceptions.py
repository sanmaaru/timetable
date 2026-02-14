from starlette import status

from app.core.exceptions import ClientError


class ThemeNotFoundError(ClientError):

    code = 'THEME_NOT_FOUND'
    status_code = status.HTTP_404_NOT_FOUND

class ColorSchemeNotFoundError(ClientError):

    code = 'COLORS_NOT_FOUND'
    status_code = status.HTTP_404_NOT_FOUND


class ThemeNotOwnedByError(ClientError):

    code = 'THEME_NOT_OWNED'
    status_code = status.HTTP_403_FORBIDDEN

class LastThemeDeleteError(ClientError):

    code = 'LAST_THEME_DELETE'
    status_code = status.HTTP_409_CONFLICT

class ThemeInUseError(ClientError):

    code = 'THEME_IN_USE'
    staus = status.HTTP_409_CONFLICT