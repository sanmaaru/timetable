from starlette import status

from app.core.exceptions import BasicError, ClientError


class InvalidFormatError(ClientError):

    code = 'INVALID_FORMAT'
    status_code = status.HTTP_400_BAD_REQUEST


class DraftNotFoundError(ClientError):

    code = 'DRAFT_NOT_FOUND'
    status_code = status.HTTP_404_NOT_FOUND


class UploadError(BasicError):
    pass


class ParseError(BasicError):
    pass
