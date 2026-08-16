from dataclasses import dataclass
from typing import Literal

SEMESTER = ['1-1', '1-2', '2-1', '2-2', '3-1', '3-2']

@dataclass
class LectureInfo:
    subject: str
    teacher: str
    room: str

    def __repr__(self) -> str:
        return f'[subject={self.subject}, teacher={self.teacher}, room={self.room}]'

    def __str__(self) -> str:
        return self.__repr__()


@dataclass
class PeriodInfo:
    subject: str
    teacher: str
    division: int
    day: int
    period: int

    def __repr__(self) -> str:
        return f'[subject={self.subject}, teacher={self.teacher}, division={self.division}, day={self.day}, period={self.period}]'

    def __str__(self) -> str:
        return self.__repr__()

@dataclass
class EnrollmentInfo:
    enroll_id: str
    name: str
    credit: int
    lectures: list[tuple[str, int, str]]  # (subject, division, teacher)

    def __repr__(self) -> str:
        return f'[enroll_id: {self.enroll_id}, name: {self.name}, subjects: {self.lectures}, credit: {self.credit}]'

    def __str__(self) -> str:
        return self.__repr__()

@dataclass
class SubjectInfo:
    subject: str
    semester: int # 1: 1-1, 2: 1-2, 3: 2-1, ... 6: 3-2
    type: Literal['공통', '선택', '자율설계']


@dataclass
class TimetableInfo:
    lectures: list[LectureInfo]
    periods: list[PeriodInfo]

@dataclass
class StudentInfo:
    name: str
    generation: int
    clazz: int
    number: int