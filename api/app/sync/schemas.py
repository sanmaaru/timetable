import ulid
from pydantic import BaseModel, field_validator


class VersionResponse(BaseModel):
    version: str

    @field_validator('version', mode='before')
    @classmethod
    def serialize_ulid(cls, v):
        if isinstance(v, ulid.ULID):
            return str(v)

        return v