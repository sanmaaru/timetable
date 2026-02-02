from datetime import datetime
from typing import List, Any

from pydantic import BaseModel, field_validator
from ulid import ULID

from theme.model import ColorScheme


def parse_color_schemes(values: list[ColorScheme]):
    color_schemes = []
    for v in values:
        color_schemes.append(ColorSchemeSchema(
            subject=v.subject.name,
            color=v.color,
            text_color=v.text_color,
        ))

    return color_schemes

class ColorSchemeSchema(BaseModel):
    subject: str
    color: str
    text_color: str


class ThemeSchema(BaseModel):

    @field_validator('theme_id', mode='before')
    @classmethod
    def serialize_ulid(cls, v: Any):
        if isinstance(v, ULID):
            return str(v)

        return v

    title: str
    published: bool
    color_schemes: List[ColorSchemeSchema]
    created_at: datetime
    updated_at: datetime
    theme_id: str
    selected: bool = False


class ThemeChangeInput(BaseModel):
    theme_id: str