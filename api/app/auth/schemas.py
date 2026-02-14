from datetime import datetime
from typing import Annotated, Any

from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict, computed_field
from ulid import ULID

class TokenPayload:
    sub: str | None = None
    iat: datetime | None = None
    exp: datetime | None = None

# === inputs ===
class SignUpInput(BaseModel):
    email: EmailStr
    username: Annotated[str, Field(min_length=3, max_length=20)]
    password: Annotated[str, Field(min_length=8)]
    identify_token: Annotated[str, Field(min_length=8, max_length=8)]


class RefreshTokenInput(BaseModel):
    refresh_token: str
    access_token: str

class LoginInput(BaseModel):
    username: str
    password: str

class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = 'bearer'

# === responses ===
class UserSchema(BaseModel):
    user_id: str
    email: str
    username: str

    model_config = ConfigDict(from_attributes=True)

    @field_validator('user_id', mode='before')
    @classmethod
    def serialize_ulid(cls, v: Any):
        if isinstance(v, ULID):
            return str(v)

        return v

class IdentifyTokenSchema(BaseModel):

    token_id: str

    user_info: Any = Field(exclude=True)

    @computed_field
    @property
    def name(self) -> str:
        return self.user_info.name

    model_config = ConfigDict(from_attributes=True)
