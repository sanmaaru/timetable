from datetime import datetime
from typing import List, Any

from pydantic import BaseModel, field_validator, ConfigDict, Field
from ulid import ULID

from app.core.types import ULIDModel


class ColorSchemeSchema(BaseModel):
    subject: str
    color: str
    text_color: str

    model_config = ConfigDict(from_attributes=True)

    @field_validator('subject', mode='before')
    @classmethod
    def serialize_subject(cls, v: Any):
        if hasattr(v, 'name'):
            return v.name

        return v


class ThemeSchema(BaseModel):
    theme_id: str
    title: str
    published: bool
    color_schemes: List[ColorSchemeSchema]
    created_at: datetime
    updated_at: datetime
    selected: bool

    model_config = ConfigDict(from_attributes=True)

    @field_validator('theme_id', mode='before')
    @classmethod
    def serialize_ulid(cls, v: Any):
        if isinstance(v, ULID):
            return str(v)

        return v

class SelectedThemeChangeInput(BaseModel):
    theme_id: ULIDModel

class ThemeChangeInput(BaseModel):
    title: str | None = None
    color_schemes: List[ColorSchemeSchema] | None = None

class ThemeCreateInput(BaseModel):
    title: str = Field(min_length=1, max_length=50, description='title')