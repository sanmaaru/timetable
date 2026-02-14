from datetime import datetime
from typing import Generic, TypeVar

from fastapi import status
from pydantic import BaseModel

from auth.model import User

T = TypeVar("T")

class MetaSchema(BaseModel):
    user_id: str
    status: int = status.HTTP_200_OK
    responded_at: datetime

class BaseResponse(BaseModel, Generic[T]):
    meta: MetaSchema
    data: T

class SuccessResponse(BaseModel):
    meta: MetaSchema

def create_response(user: User, data: T, status_code: int = status.HTTP_200_OK):
    return BaseResponse(
        meta = MetaSchema(
            user_id = str(user.user_id),
            status=status_code,
            responded_at=datetime.now(),
        ),
        data = data
    )