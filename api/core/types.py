from typing import Any, Annotated

import ulid
from fastapi.exceptions import RequestValidationError
from pydantic import BeforeValidator, PlainSerializer, WithJsonSchema
from ulid import ULID


## ==== ULID ====
def validate_ulid(v: Any) -> ULID | None:
    if v is None:
        return None

    if isinstance(v, ULID):
        return v

    try:
        return ulid.from_str(v)
    except ValueError:
        raise RequestValidationError('invalid ulid value')

def serialize_ulid(v: ULID) -> str:
    return str(v)

ULIDInput = Annotated[
    str,
    BeforeValidator(validate_ulid),
    PlainSerializer(serialize_ulid, return_type=str),
    WithJsonSchema({'type': 'string', 'example': '01KG7NGMX0QVK86MZKQ1QR8XJJ'}),
]