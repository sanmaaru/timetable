import re
from typing import Literal, List, Optional, Annotated

import et_xmlfile
from pandas.core.computation import expr
from pydantic import BaseModel, RootModel, Field, field_validator, AfterValidator

from app.core.types import ULIDModel

# ===== Common Classes =====
PATTERN = re.compile(r"^[0-9][0-9]{2}-[0-9a-fA-f]{12}$")

def validate_identity_id_format(v: str) -> str:
    if len(v) != 16 or not PATTERN.match(v):
        raise ValueError("유효하지 않은 IdentityId 포맷입니다 (16자리, 첫글자 숫자).")
    return v

IdentityIdStr = Annotated[str, AfterValidator(validate_identity_id_format)]


# ===== Router Schemas =====
class UploadConfirmInput(BaseModel):
    draft_id: ULIDModel = Field(..., description='Draft의 ULID')
    mode: Literal['overwrite', 'rewrite'] = Field(
        ...,
        description='데이터 입력 모드, overwrite는 기존데이터를 덮어쓰고, rewrite는 데이터를 전체 삭제한 뒤에 새로 작성한다',
        examples=['overwrite', 'rewrite']
    )
    confirm: bool = Field(..., description='Draft를 적용할지 여부')

class UploadResponse(BaseModel):
    draft_id: str = Field(..., description='Draft의 ULID')
    is_exist: bool = Field(..., description='데이터베이스에 데이터가 이미 존재하는지 여부')

# ===== Json File Schemas =====
class SubjectFileSchema(RootModel[List[str]]):
    pass

class LectureInfoSchema(BaseModel):
    subject: str = Field(..., description='과목명', examples=['동물생리학'])
    teacher: Optional[str] = Field(..., description='선생님 이름', examples=['신성현'])
    room: Optional[str] = Field(None, description='강의실', examples=['3-6 교실'])
    division: int = Field(..., description='분반', examples=[2])


class LectureListSchema(RootModel[List[LectureInfoSchema]]):
    pass

class PeriodSchema(BaseModel):
    day: int = Field(..., description='요일 (1: 월요일, 2: 화요일, ...)', examples=[1, 2])
    period: int = Field(..., description='교시', examples=[1, 2])

class PeriodInfoSchema(BaseModel):
    lecture: LectureInfoSchema
    period: PeriodSchema

class PeriodListSchema(RootModel[List[PeriodInfoSchema]]):
    pass

class EnrollmentUserInfoSchema(BaseModel):
    identity_id: IdentityIdStr
    name: str
    credit: int

class EnrollmentInfoSchema(BaseModel):
    lectures: List[LectureInfoSchema]
    student: EnrollmentUserInfoSchema

class EnrollmentListSchema(RootModel[List[EnrollmentInfoSchema]]):
    pass

class StudentInfoSchema(BaseModel):
    name: str
    generation: int
    clazz: int
    number: int
    identity_id: IdentityIdStr


class StudentInfoListSchema(RootModel[List[StudentInfoSchema]]):
    pass

class TeacherInfoSchema(BaseModel):
    name: str
    identity_id: IdentityIdStr

class TeacherInfoListSchema(RootModel[List[TeacherInfoSchema]]):
    pass