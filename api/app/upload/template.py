import copy
from itertools import chain

import numpy as np
import pandas as pd

from app.upload.exceptions import ParseError
from app.upload.schema import EnrollmentInfo, PeriodInfo, LectureInfo
from app.util.common import is_empty, get_generation


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
        it = it.strip()
        if len(it) != 5 or not it.isdigit():
            return False
        
        return True

    
    def interpret(self, content) -> tuple[int, int, int, str]:
        it, _, name = content.partition(" ")

        grade, cls, num = int(it[0]), int(it[1:3]), int(it[3:])
        return get_generation(grade), cls, num, name
    
    def name(self) -> str:
        return StudentCell.__type__


class CreditCell(Cell[int]):

    __type__ = 'credit'

    def match(self, content: str) -> bool:
        it, _, suffix = content.partition(" ")
        it = it.strip()
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
        div = div.strip()
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
            divided = content.replace(")", "").split("(")
            if len(divided) < 2:
                return False

            if not divided[1].replace("분반", "").strip().isdigit():
                return False
            
            for period in divided[0].split(','):
                if not period.strip().isdigit():
                    return False

        return True
        
        

    def interpret(self, content: str) -> list[tuple[int, int]]:
        contents = content.split("\n")
        result = []
        for content in contents:
            divided = content.replace(")", "").split("(")
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

    
def parse_enrollments(path: str) -> tuple[list[EnrollmentInfo], list[PeriodInfo]]:
    board = get_board(path)
    data = template.convolute(board)
    student_info_list = []
    period_info_list = []
    for _, contents in data.items():
        organized = {}
        for j, row_content in enumerate(contents):
            for i, type_content in enumerate(row_content):
                type = type_content[0]
                content = type_content[1]
                if not content:
                    continue
                
                if type == 'class':
                    period_info = PeriodInfo(subject=content[0], teacher="Unknown", division=content[1], day=i+1, period=j)
                    if period_info not in period_info_list:
                        period_info_list.append(period_info)

                if type in organized:
                    if not isinstance(organized[type], list):
                        organized[type] = [organized[type]]

                    if content not in organized[type]:
                        organized[type].append(content)

                    continue

                organized[type] = content

        student = organized['student']
        classes = organized['class']
        credit = organized['credit']
        if not isinstance(classes, list):
            classes = [classes]

        student_info = EnrollmentInfo(
            student[0],
            student[1],
            student[2],
            student[3],
            credit,
            classes
        )
        student_info_list.append(student_info)

    return student_info_list, period_info_list


def find(type: str, contents):
    for cell_type, content in contents:
        if cell_type == type:
            return content

    return None

def parse_lectures(path: str) -> list[LectureInfo]:
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
                    raise ParseError(f'room is none', teacher=content)
                
                lecture_info = LectureInfo(subject=subject, teacher=content, room=room)
                if lecture_info not in lecture_info_list:
                    lecture_info_list.append(lecture_info)

    return lecture_info_list


PERIOD_START_COL = 2
def parse_periods(path: str) -> list[PeriodInfo]:
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
                if content is None:
                    subject = subject_cache
                    continue
                
                subject = content
                subject_cache = subject
            
            if type == 'teacher':
                if content is None:
                    continue

                teacher = content

            if type == 'period':
                if content is None:
                    continue

                day = idx - (PERIOD_START_COL - 1)
                for division, p in content:
                    periods.append((division, day, p))


        for period in periods:
            period_info = PeriodInfo(subject=subject, teacher=teacher, division=period[0], day=period[1], period=period[2]) 
            period_info_list.append(period_info)

    return period_info_list

# TODO: 추후에 엑셀을 다듬는 프로그램을 새로 만들어야 할 듯
def unify_periods(periods: list[PeriodInfo], muti_tch_period: list[PeriodInfo], lectures: list[LectureInfo]) -> list[PeriodInfo]:
    period_info_list = copy.deepcopy(muti_tch_period)
    multi_tch_subject = []
    for period in muti_tch_period:
        multi_tch_subject.append(period.subject)

    subject_teacher_map = {}
    for lecture in lectures:
        if lecture.subject in multi_tch_subject:
            continue

        subject_teacher_map[lecture.subject] = lecture.teacher

    for period in periods:
        if period.subject in multi_tch_subject:
            continue

        period.teacher = subject_teacher_map[period.subject]
        period_info_list.append(period)
    
    return period_info_list