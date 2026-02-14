from datetime import datetime, timezone
from typing import Generic, TypeVar

from fastapi import status
from pydantic import BaseModel, Field
from ulid.ulid import ULID

from app.auth.model import User

T = TypeVar("T")

class MetaSchema(BaseModel):
    user_id: str
    status: int = status.HTTP_200_OK
    responded_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class BaseResponse(BaseModel, Generic[T]):
    meta: MetaSchema
    data: T

class SuccessResponse(BaseModel):
    meta: MetaSchema

def create_response(data: T, user_id: ULID = None, status_code: int = status.HTTP_200_OK):
    return BaseResponse(
        meta = MetaSchema(
            user_id = str(user_id) if user_id else None,
            status=status_code,
        ),
        data = data
    )