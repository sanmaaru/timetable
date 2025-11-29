from sqlalchemy.orm.session import Session
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import SQLAlchemyError
from database import User, Class, Subject, Lecture, Period, Enrollment
from dataclasses import dataclass
from util import is_empty
from itertools import chain
import numpy as np
import pandas as pd
import re

# __all__ = ['upload_students', 'upload_teachers']

class Cell[T]:

    def match(self, content: str) -> bool:
        raise NotImplementedError()

    def interpret(self, content: str) -> T:
        raise NotImplementedError() 

    def name(self) -> str:
        raise NotImplementedError()

    def __len__(self) -> int:
        return 1      


class StudentCell(Cell[tuple[int, int, int, str]]):

    __type__ = 'student'

    def match(self, content) -> bool:
        it, _, name = content.partition(" ")
        if len(it) != 5 or not it.isdigit():
            return False
        
        return True

    
    def interpret(self, content) -> tuple[int, int, int, str]:
        it, _, name = content.partition(" ")

        grade, cls, num = int(it[0]), int(it[1:3]), int(it[3:])
        return grade, cls, num, name
    
    def name(self) -> str:
        return StudentCell.__type__


class CreditCell(Cell[int]):

    __type__ = 'credit'

    def match(self, content: str) -> bool:
        it, _, suffix = content.partition(" ")
        if suffix != '학점' or not it.isdigit():
            return False

        return True
    
    def interpret(self, content: str) -> int:
        it, _, _ = content.partition(" ")
        return int(it)
    
    def name(self) -> str:
        return CreditCell.__type__


class ClassCell(Cell[tuple[str, int]]):

    __type__ = 'class'

    def match(self, content: str) -> bool:
        sep = content.split(" ")
        if len(sep) < 3:
            return False

        div = content.split(" ")[-2]
        div, suffix = div[:-1], div[-1]
        if suffix != '반' or not div.isdigit():
            return False
        
        return True
    
    def interpret(self, content: str) -> tuple[str, int]:
        div = content.split(" ")[-2]
        div, _ = div[:-1], div[-1]
        lec = " ".join(content.split(" ")[:-2])
        return lec, int(div)
    
    def name(self) -> str:
        return ClassCell.__type__
    

class EmptyCell(Cell[None]):

    def match(self, content) -> bool:
        return is_empty(content)

    def interpret(self, content) -> None:
        return None
    
    def name(self) -> str:
        return "empty"

class SubjectCell(Cell[str]):

    __type__ = 'subject'

    def match(self, content: str) -> bool:
        return not is_empty(content)
    
    def interpret(self, content: str) -> str:
        return content
    
    def name(self) -> str:
        return SubjectCell.__type__

class TeacherCell(Cell[str]):

    __type__ = 'teacher'

    def match(self, content: str) -> bool:
        return not is_empty(content)
    
    def interpret(self, content: str) -> str:
        return content
    
    def name(self) -> str:
        return TeacherCell.__type__

class RoomCell(Cell[str]):

    __type__ = 'room'

    def match(self, content: str) -> bool:
        return not is_empty(content)
    
    def interpret(self, content: str) -> str:
        return content
    
    def name(self) -> str:
        return RoomCell.__type__

class PeriodCell(Cell[list[tuple[int, int]]]):

    __type__ = 'period'

    def match(self, content: str) -> bool: # TODO: 정규식 사용
        contents = content.split("\n")
        for content in contents:
            divided = content[:-1].split("(")
            if len(divided) < 2:
                return False

            if not divided[1].replace("분반", "").isdigit():
                return False
            
            for period in divided[0].split(','):
                if not period.isdigit():
                    return False

        return True
        
        

    def interpret(self, content: str) -> list[tuple[int, int]]:
        contents = content.split("\n")
        result = []
        for content in contents:
            divided = content[:-1].split("(")
            division = int(divided[1].replace("분반", ""))
            periods = list(map(int, divided[0].split(",")))
            for period in periods:
                result.append((division, period))
        return result       
            
    
    def name(self) -> str:
        return self.__type__

class DelegateCell(Cell):

    def __init__(self, *cells):
        self.cells = cells

    def match(self, content: str) -> bool:
        for cell in self.cells:
            if cell.match(content):
                return True
        return False       
    
    def interpret(self, content: str) -> object:
        for cell in self.cells:
            if cell.match(content):
                return cell.interpret(content)

        raise ValueError()
    
    def name(self) -> str:
        return self.cells[0].name()


## ===== Template ======
class Template:

    def __init__(self, template: list[list[Cell]]):
        self.template = template
        self.width = len(template[0])
        self.height = len(template)

    def match_at(self, board: np.ndarray, x, y) -> bool:
        h, w = board.shape
        for j in range(self.height):
            for i in range(self.width):
                cell = self.template[j][i]
                if x + i >= w or y + j >= h:
                    content = ""
                else:
                    content = str(board[y+j][x+i])
                
                if not cell.match(content):
                    return False
        return True

    def stamp(self, board: np.ndarray, x, y) -> list[list]:
        if not self.match_at(board, x, y):
            return []
        
        h, w = board.shape 
        contents = []
        for j in range(self.height):
            contents_row = []
            for i in range(self.width):
                if x + i >= w or y + j >= h:
                    continue

                cell = self.template[j][i]
                
                content = str(board[y+j][x+i])
                
                content = cell.interpret(content)

                contents_row.append((cell.name(), content))

            contents.append(contents_row)
        return contents


    def convolute(self, board: np.ndarray) -> dict[tuple[int], list[list]]:
        h, w = board.shape
        if h < self.height or w < self.width :
            return {}

        result = {}        
        for j in range(h - self.height + 1):
            for i in range(w - self.width + 1):
                stamp = self.stamp(board, i, j)
                if not stamp:
                    continue

                result[(i, j)] = stamp
        
        return result


## ===== Template for Timetable =====
EMPTY = EmptyCell()
NAME = StudentCell()
CREDIT = CreditCell()
CLASS = DelegateCell(ClassCell(), EMPTY) # 공강 확인
NONE = EmptyCell()

TEACHER = DelegateCell(TeacherCell(), EMPTY)
ROOM = DelegateCell(RoomCell(), EMPTY)
SUBJECT = SubjectCell()
PERIOD = DelegateCell(PeriodCell(), EMPTY)

template = Template([[NAME, CREDIT, NONE, NONE, NONE],
                     [CLASS, CLASS, CLASS, CLASS, CLASS],
                     [CLASS, CLASS, CLASS, CLASS, CLASS],
                     [CLASS, CLASS, CLASS, CLASS, CLASS],
                     [CLASS, CLASS, CLASS, CLASS, CLASS],
                     [CLASS, CLASS, CLASS, CLASS, CLASS],
                     [CLASS, CLASS, CLASS, CLASS, CLASS],
                     [CLASS, CLASS, CLASS, CLASS, CLASS],
                     [CLASS, CLASS, CLASS, CLASS, CLASS]])

template_room = Template([[SUBJECT, TEACHER, ROOM, TEACHER, ROOM, TEACHER, ROOM]])

template_period = Template([[DelegateCell(SUBJECT, EMPTY), TEACHER, PERIOD, PERIOD, PERIOD, PERIOD, PERIOD]])

## ===== Parsing Logic =====
def get_board(path):
    df = pd.read_excel(path)
    board = df.to_numpy()

    return board

class ParseError(Exception):
    pass

@dataclass
class StudentInfo:
    grade: int
    clazz: int
    number: int
    name: str
    subjects: list[tuple[str, int]] # (subject, division)

    def __repr__(self) -> str:
        return f'[grade: {self.grade}, clazz: {self.clazz}, number: {self.number}, name: {self.name}, subjects: {self.subjects}]'
    
    def __str__(self) -> str:
        return self.__repr__()

def parse_student(path: str) -> list[StudentInfo]:
    board = get_board(path)
    data = template.convolute(board)
    student_info_list = []
    for _, contents in data.items():
        organized = {}
        contents = list(chain.from_iterable(contents))
        for type, content in contents:
            if not content:
                continue

            if type in organized:
                if not isinstance(organized[type], list):
                    organized[type] = [organized[type]]
                organized[type].append(content)
                continue

            organized[type] = content

        student = organized['student']
        classes = organized['class']
        if not isinstance(classes, list):
            classes = [classes]

        student_info = StudentInfo(
            student[0],
            student[1],
            student[2],
            student[3],
            classes
        )
        student_info_list.append(student_info)

    return student_info_list

@dataclass
class LectureInfo:
    subject: str
    teacher: str
    room: str

    def __repr__(self) -> str:
        return f'[subject={self.subject}, teacher={self.teacher}, room={self.room}]'
    
    def __str__(self) -> str:
        return self.__repr__()

def find(type: str, contents):
    for cell_type, content in contents:
        if cell_type == type:
            return content

    return None

def parse_lecture(path: str) -> list[LectureInfo]:
    board = get_board(path)
    data = template_room.convolute(board)
    lecture_info_list = []
    for _, contents in data.items():
        contents = list(chain.from_iterable(contents))
        subject = str(find('subject', contents)).strip().replace("\n", "")
        for idx, (type, content) in enumerate(contents):
            if not content:
                continue

            if type == 'teacher':
                room = contents[idx+1][1]
                if not room:
                    raise ParseError(f'[teacher={content}] room is none')
                
                lecture_info = LectureInfo(subject=subject, teacher=content, room=room)
                if lecture_info not in lecture_info_list:
                    lecture_info_list.append(lecture_info)

    return lecture_info_list

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

PERIOD_START_COL = 2
def parse_period(path: str) -> list[PeriodInfo]:
    board = get_board(path)
    data = template_period.convolute(board)
    period_info_list = []
    subject_cache = "None" # if subject is none, use latest subject
    for _, contents in data.items():
        contents = list(chain.from_iterable(contents))
        subject, teacher, periods = "", "", []
        for idx, type_content in enumerate(contents):
            type = type_content[0]
            content = type_content[1]
            if type == 'subject':
                if content == None:
                    subject = subject_cache
                    continue
                
                subject = content
                subject_cache = subject
            
            if type == 'teacher':
                if content == None:
                    continue

                teacher = content

            if type == 'period':
                if content == None:
                    continue

                day = idx - (PERIOD_START_COL - 1)
                for division, p in content:
                    periods.append((division, day, p))


        for period in periods:
            period_info = PeriodInfo(subject=subject, teacher=teacher, division=period[0], day=period[1], period=period[2]) 
            period_info_list.append(period_info)

    return period_info_list


## ===== Upload Logic =====
class UploadError(Exception):
    pass

def upload_students(students: list[StudentInfo], session: Session):
    try:
        cache = {} # cache of subject_name and division of student
        for student in students:
            db_student = session.query(User).filter(
                User.grade == student.grade,
                User.clazz == student.clazz, 
                User.number == student.number, 
                User.name == student.name).one_or_none()
            if db_student == None:
                raise UploadError(f'{student} cannot find student')
        

            # refactor with join
            for subject_name, division in student.subjects:
                if (subject_name, division) not in cache:
                    classes = (session.query(Class).join(Class.lecture).join(Lecture.subject)
                            .filter(Class.division == division, Subject.name == subject_name)
                            .options(joinedload(Class.lecture).joinedload(Lecture.subject))
                            .all())
                    
                    if len(classes) > 1:
                        raise UploadError(f'[subject={subject_name}, division={division}] multiple classes')

                    if len(classes) == 0:
                        raise UploadError(f'[subject={subject_name}, division={division}] cannot find class')
                    
                    cache[(subject_name, division)] = classes[0].class_id

                class_id = cache[(subject_name, division)]
                enrollment = Enrollment(class_id=class_id, user_id=db_student.user_id)
                session.add(enrollment)
        session.commit()
    except (UploadError, SQLAlchemyError):
        session.rollback()
        raise 
            

def upload_lecture(lectures: list[LectureInfo], session: Session):
    try:
        for lecture in lectures:
        
            # create subject if not the subject exists
            subject = session.query(Subject).filter(Subject.name == lecture.subject).one_or_none()
            if subject == None:
                subject = Subject(name=lecture.subject)
                session.add(subject)
                session.flush()

            # create lecture
            teacher_name = lecture.teacher.split(",")[0].strip()
            teacher = session.query(User).filter(User.name == teacher_name, User.role == 'tch').one_or_none()
            if teacher == None:
                raise UploadError(f'{lecture} cannot find teacher')

            # confirm multiplicity
            db_lecture = session.query(Lecture).filter(
                Lecture.subject_id == subject.subject_id, 
                Lecture.teacher_id == teacher.user_id,
                Lecture.room == lecture.room
            ).one_or_none()
            if db_lecture != None:
                continue

            lecture = Lecture(subject_id=subject.subject_id, teacher_id=teacher.user_id, room=lecture.room)
            session.add(lecture)

        session.commit()
    except (UploadError, SQLAlchemyError):
        session.rollback()
        raise
            

def upload_periods(periods: list[PeriodInfo], session: Session):
    try:
        cache = {}
        for period in periods:
            teacher_name = period.teacher.split(',')[0].strip()

            if (period.subject, teacher_name) not in cache:
                # Lecture 가져오기
                lecture = (session.query(Lecture).join(Lecture.subject).join(Lecture.teacher)
                           .filter(Subject.name == period.subject, User.name == teacher_name)
                           .options(joinedload(Lecture.subject), joinedload(Lecture.teacher))
                           .all())
            
                if len(lecture) > 1:
                    raise UploadError(f'{period} too many lectures')
                elif len(lecture) == 0:
                    raise UploadError(f'{period} cannot find lecture')
                
                cache[(period.subject, teacher_name)] = lecture[0].lecture_id
            
            lecture_id = cache[(period.subject, teacher_name)]

            clazz = session.query(Class).where(Class.lecture_id == lecture_id,
                                                       Class.division == period.division).one_or_none()
            if clazz == None:
                clazz = Class(lecture_id=lecture_id, division=period.division)
                session.add(clazz)
                session.flush()
                    
            period = Period(class_id=clazz.class_id, period=period.period, day=period.day)
            session.add(period)
        session.commit()
    except (UploadError, SQLAlchemyError):
        session.rollback()
        raise


if __name__ == '__main__':
    board = get_board('2025 선생님.xlsx')
    # print(board)
    # print(template_teacher.stamp(board, 1, 1))
    for idx, data in template_period.convolute(board).items():
        content = data
        print(content)
    
    print("\n".join(map(str, parse_student('2025 2학기 2,3학년 시간표(시간표조회).xlsx'))))