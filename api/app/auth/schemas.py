from dataclasses import dataclass
from datetime import datetime
from typing import Annotated, Any

from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict
from ulid import ULID

from app.core.config import configs


@dataclass
class TokenPayload:
    sub: str | None
    iat: datetime | None
    exp: datetime | None

@dataclass
class UserInfoData:
    name: str
    generation: int | None = None
    clazz: int | None = None
    number: int | None = None
    credit: int | None = None

# === inputs ===
class SignUpInput(BaseModel):
    email: EmailStr
    username: Annotated[str, Field(min_length=3, max_length=20)]
    password: Annotated[str, Field(min_length=8)]
    identify_token: Annotated[str, Field(min_length=configs.ID_TOKEN_LENGTH, max_length=configs.ID_TOKEN_LENGTH)]


class RefreshTokenInput(BaseModel):
    refresh_token: str

class LoginInput(BaseModel):
    username: str
    password: str

class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = 'bearer'

    @field_validator('refresh_token', mode='before')
    @classmethod
    def serialize_ulid(cls, v: Any):
        if isinstance(v, ULID):
            return str(v)

        return v

# === schemas ===
class UserInfoSchema(BaseModel):
    name: str
    generation: int | None
    clazz: int | None
    number: int | None
    credit: int | None
    role: int
    identity_id: str

    @field_validator('user_info_id', mode='before')
    @classmethod
    def serialize_ulid(cls, v: Any):
        if isinstance(v, ULID):
            return str(v)

        return v

    model_config = ConfigDict(from_attributes=True)


class UserSchema(BaseModel):
    user_id: str | None
    email: str | None
    username: str | None
    identity_id: str

    user_info: UserInfoSchema | None

    model_config = ConfigDict(from_attributes=True)

    @field_validator('user_id', mode='before')
    @classmethod
    def serialize_ulid(cls, v: Any):
        if isinstance(v, ULID):
            return str(v)

        return v


class IdentifyTokenSchema(BaseModel):

    token_id: str
    identity_id: str
    expired: bool

    model_config = ConfigDict(from_attributes=True)
