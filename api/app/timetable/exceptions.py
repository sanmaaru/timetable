from starlette import status

from app.core.exceptions import ClientError


class UnknownClassError(ClientError):

    status_code = status.HTTP_404_NOT_FOUND
    code = 'UNKNOWN_CLASS'

class SemesterNotSelectedError(ClientError):

    status_code = status.HTTP_400_BAD_REQUEST
    code = 'SEMESTER_NOT_SELECTED'