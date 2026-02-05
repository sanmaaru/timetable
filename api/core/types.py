from typing import Any

import ulid
from pydantic import GetCoreSchemaHandler
from pydantic_core import core_schema


class ULIDModel(ulid.ULID):

    @classmethod
    def __get_pydantic_core_schema__(
            cls, source_type: Any, handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:
        return core_schema.json_or_python_schema(
            json_schema=core_schema.str_schema(),
            python_schema=core_schema.no_info_after_validator_function(
                cls.validate,
                core_schema.str_schema()
            ),
            serialization=core_schema.plain_serializer_function_ser_schema(str),
        )

    @classmethod
    def validate(cls, v: str):
        try:
            return ulid.from_str(v)
        except ValueError:
            raise ValueError("Invalid ULID format")

