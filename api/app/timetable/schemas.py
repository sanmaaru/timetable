from typing import List, Any

import ulid.ulid
from pydantic import BaseModel, ConfigDict, Field, computed_field
from pydantic import field_validator

from app.auth.schemas import UserSchema, UserInfoSchema
from app.timetable.model import Period


#

class PeriodSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    period: int
    day: str = Field(alias="day")  # JSON에서는 'day'로 보임

    @field_validator("day", mode="before")
    @classmethod
    def convert_day_index(cls, v: Any):
        # 인덱스(0~6)를 'Sun', 'Mon' 등으로 변환
        if isinstance(v, int):
            return Period.DAY[v]
        return v


class ClassSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    class_id: str
    division: int
    periods: List[PeriodSchema]
    classmates: List[UserInfoSchema]

    lecture: Any = Field(exclude=True)

    # 중첩된 관계에서 데이터 추출 (Flattening)
    @computed_field
    @property
    def subject(self) -> str:
        return self.lecture.subject.name

    @computed_field
    @property
    def teacher(self) -> str:
        return self.lecture.teacher_info.name

    @computed_field
    @property
    def room(self) -> str:
        return self.lecture.room

    @field_validator("class_id", mode="before")
    @classmethod
    def serialize_ulid(cls, v: Any):
        if isinstance(v, ulid.ULID):
            return str(v)

        return v


class TimetableSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    username: str
    name: str
    timetable: List[ClassSchema]