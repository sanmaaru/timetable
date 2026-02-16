from dataclasses import dataclass


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
    generation: int
    clazz: int
    number: int
    name: str
    credit: int
    subjects: list[tuple[str, int]]  # (subject, division)

    def __repr__(self) -> str:
        return (f'[generation: {self.generation}, clazz: {self.clazz}, number: {self.number},'
                f' name: {self.name}, subjects: {self.subjects}, credit: {self.credit}]')

    def __str__(self) -> str:
        return self.__repr__()

