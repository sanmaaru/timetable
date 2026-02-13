from datetime import datetime
from typing import List

from pydantic import BaseModel

class ColorSchemeSchema(BaseModel):
    subject: str
    color: str
    text_color: str


class ThemeSchema(BaseModel):
    title: str
    published: bool
    color_schemas: List[ColorSchemeSchema]
    created_at: datetime
    updated_at: datetime
    theme_id: str


class ThemeChangeInput(BaseModel):
    theme_id: str