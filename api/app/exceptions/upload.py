from starlette import status

from app.core.exceptions import BasicError, ClientError


class InvalidFormatError(ClientError):

    code = 'INVALID_FORMAT'
    status_code = status.HTTP_400_BAD_REQUEST


class UploadError(ClientError):

    code = 'UPLOAD_ERROR'
    status_code = status.HTTP_400_BAD_REQUEST

    pass
