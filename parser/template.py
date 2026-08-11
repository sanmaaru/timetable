import copy
import re
from itertools import chain

import math
import numpy as np
import pandas as pd

from schema import EnrollmentInfo, PeriodInfo, LectureInfo, SubjectInfo, TimetableInfo, StudentInfo, SEMESTER
from util import is_empty, get_generation


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

    
    def interpret(self, content) -> tuple[str, str]:
        it, _, name = content.partition(" ")

        return it, name
    
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

class SkippedCell(Cell[None]):

    def match(self, content) -> bool:
        return True

    def interpret(self, content: str) -> None:
        return None

    def name(self) -> str:
        return "skipped"

class SubjectCell(Cell[str]):

    __type__ = 'subject'

    def match(self, content: str) -> bool:
        return not is_empty(content)
    
    def interpret(self, content: str) -> str:
        if content.startswith('자설-'):
            content = content.replace('자설-', '')

        content = re.sub(r'[A-Za-z1-9]$', '', content)

        return content
    
    def name(self) -> str:
        return SubjectCell.__type__

class TeacherCell(Cell[str]):

    __type__ = 'teacher'

    def match(self, content: str) -> bool:
        return not is_empty(content)
    
    def interpret(self, content: str) -> str:
        content = content.replace('\n', ', ')

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


class SubjectTypCell(Cell[str]):

    types = ['공통', '선택', '자율설계']

    __type__ = 'subject_type'

    def match(self, content: str) -> bool:
        return content.strip() in self.types


    def interpret(self, content: str) -> str:
        return content.strip()


    def name(self) -> str:
        return self.__type__


class StudentNumberCell(Cell[tuple[int, int ,int]]):

    __type__ = 'student_number'

    def match(self, content: str) -> bool:
        try:
            grade, clazz, number = int(content[0]), int(content[1:3]), int(content[3:])
            assert 0 < grade <= 3
        except Exception as e:
            return False

        return True


    def interpret(self, content: str) -> tuple[int, int, int]:
        grade = int(content[0])
        clazz = int(content[1:3])
        number = int(content[3:])

        return grade, clazz, number

    def name(self) -> str:
        return self.__type__


class RegexCell[T](Cell[T]):

    __type__ = 'regex'

    def __init__(self, regex: str, name: str):
        self.regex = regex
        self.__type__ = name

    def match(self, content: str) -> bool:
        match = re.match(self.regex, content)
        return match is not None and len(match.groups()) != 0

    def interpret(self, content: str) -> T:
        match = re.match(self.regex, content)
        if not match:
            return None

        matches = match.groups()
        return matches if len(matches) > 1 else matches[0]

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


class MarkingCell(Cell[bool]):

    def match(self, content: str) -> bool:
        return True

    def interpret(self, content: str) -> bool:
        return not is_empty(content)

    def name(self):
        return 'marking'


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
                
                content = str(board[y+j][x+i]).strip()
                
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
SKIPPED = SkippedCell()
MARKING = MarkingCell()


NAME = StudentCell()
CREDIT = CreditCell()
CLASS = DelegateCell(ClassCell(), EMPTY) # 공강 확인
TEACHER = DelegateCell(TeacherCell(), EMPTY)
ROOM = DelegateCell(RoomCell(), EMPTY)
SUBJECT = SubjectCell()
NULLABLE_SUBJECT = DelegateCell(SubjectCell(), EMPTY)
SUBJECT_TYPE = SubjectTypCell()
PERIOD = DelegateCell(PeriodCell(), EMPTY)

SECTION = RegexCell(r'^(\d{1,2})-(\d)$', 'section')
DAY = RegexCell(r'([월화수목금])', 'day')

STUDENT_NAME = RegexCell(r'^([\s\S]*)$', 'name')
STUDENT_NUMBER = StudentNumberCell()

template = Template([[NAME, CREDIT, EMPTY, EMPTY, EMPTY],
                     [CLASS, CLASS, CLASS, CLASS, CLASS],
                     [CLASS, CLASS, CLASS, CLASS, CLASS],
                     [CLASS, CLASS, CLASS, CLASS, CLASS],
                     [CLASS, CLASS, CLASS, CLASS, CLASS],
                     [CLASS, CLASS, CLASS, CLASS, CLASS],
                     [CLASS, CLASS, CLASS, CLASS, CLASS],
                     [CLASS, CLASS, CLASS, CLASS, CLASS]])

template_room = Template([[SUBJECT, TEACHER, ROOM, TEACHER, ROOM, TEACHER, ROOM]])

template_period = Template([[DelegateCell(SUBJECT, EMPTY), TEACHER, PERIOD, PERIOD, PERIOD, PERIOD, PERIOD]])

template_subject = Template([[SKIPPED, SKIPPED, SKIPPED, SUBJECT_TYPE, SUBJECT, SKIPPED, SKIPPED, MARKING, MARKING, MARKING, MARKING, MARKING, MARKING]])

template_timetable = Template([
    [SKIPPED, SKIPPED, SKIPPED, SECTION, SKIPPED, SKIPPED],
    [EMPTY, DAY, DAY, DAY, DAY, DAY],
    [SKIPPED, NULLABLE_SUBJECT, NULLABLE_SUBJECT, NULLABLE_SUBJECT, NULLABLE_SUBJECT, NULLABLE_SUBJECT],
    [SKIPPED, TEACHER, TEACHER, TEACHER, TEACHER, TEACHER],
    [SKIPPED, ROOM, ROOM, ROOM, ROOM, ROOM],
    [SKIPPED, NULLABLE_SUBJECT, NULLABLE_SUBJECT, NULLABLE_SUBJECT, NULLABLE_SUBJECT, NULLABLE_SUBJECT],
    [SKIPPED, TEACHER, TEACHER, TEACHER, TEACHER, TEACHER],
    [SKIPPED, ROOM, ROOM, ROOM, ROOM, ROOM],
    [SKIPPED, NULLABLE_SUBJECT, NULLABLE_SUBJECT, NULLABLE_SUBJECT, NULLABLE_SUBJECT, NULLABLE_SUBJECT],
    [SKIPPED, TEACHER, TEACHER, TEACHER, TEACHER, TEACHER],
    [SKIPPED, ROOM, ROOM, ROOM, ROOM, ROOM],
    [SKIPPED, NULLABLE_SUBJECT, NULLABLE_SUBJECT, NULLABLE_SUBJECT, NULLABLE_SUBJECT, NULLABLE_SUBJECT],
    [SKIPPED, TEACHER, TEACHER, TEACHER, TEACHER, TEACHER],
    [SKIPPED, ROOM, ROOM, ROOM, ROOM, ROOM],
    [SKIPPED, NULLABLE_SUBJECT, NULLABLE_SUBJECT, NULLABLE_SUBJECT, NULLABLE_SUBJECT, NULLABLE_SUBJECT],
    [SKIPPED, TEACHER, TEACHER, TEACHER, TEACHER, TEACHER],
    [SKIPPED, ROOM, ROOM, ROOM, ROOM, ROOM],
    [SKIPPED, NULLABLE_SUBJECT, NULLABLE_SUBJECT, NULLABLE_SUBJECT, NULLABLE_SUBJECT, NULLABLE_SUBJECT],
    [SKIPPED, TEACHER, TEACHER, TEACHER, TEACHER, TEACHER],
    [SKIPPED, ROOM, ROOM, ROOM, ROOM, ROOM],
    [SKIPPED, NULLABLE_SUBJECT, NULLABLE_SUBJECT, NULLABLE_SUBJECT, NULLABLE_SUBJECT, NULLABLE_SUBJECT],
    [SKIPPED, TEACHER, TEACHER, TEACHER, TEACHER, TEACHER],
    [SKIPPED, ROOM, ROOM, ROOM, ROOM, ROOM],
])

template_student = Template([[STUDENT_NUMBER, STUDENT_NAME]])

## ===== Parsing Logic =====
def get_board(path):
    df = pd.read_excel(path, header=None)
    board = df.to_numpy()

    return board

    
def parse_enrollments(path: str) -> list[EnrollmentInfo]:
    board = get_board(path)
    data = template.convolute(board)
    student_info_list = []
    for _, contents in data.items():
        organized = {}
        for row_content in contents:
            for type_content in row_content:
                type = type_content[0]
                content = type_content[1]
                if not content:
                    continue

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
            credit,
            classes
        )
        student_info_list.append(student_info)

    return student_info_list


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
                    raise ValueError(f'room is none teacher={content}')
                
                lecture_info = LectureInfo(subject=subject, teacher=content, room=room)
                if lecture_info not in lecture_info_list:
                    lecture_info_list.append(lecture_info)

    return lecture_info_list

def parse_division(path: str) -> dict[str, int]:
    board = get_board(path)
    data = template.convolute(board)
    subject_division_map = {}
    for _, contents in data.items():
        for row_content in contents:
            for type_content in row_content:
                type = type_content[0]
                content = type_content[1]

                if type != 'class' or content is None:
                    continue

                subject = content[0]
                division = content[1]

                subject_division_map[subject] = max(subject_division_map.get(subject, 0), division)

    return subject_division_map


PERIOD_START_COL = 2
def parse_multi_tch_periods(path: str) -> list[PeriodInfo]:
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

def parse_periods(path: str) -> list[PeriodInfo]:
    board = get_board(path)
    data = template.convolute(board)
    period_info_list = []
    for _, contents in data.items():
        for j, row_content in enumerate(contents):
            for i, type_content in enumerate(row_content):
                type = type_content[0]
                content = type_content[1]
                if not content:
                    continue

                if type == 'class':
                    period_info = PeriodInfo(subject=content[0], teacher="Unknown", division=content[1], day=i + 1,
                                             period=j)
                    if period_info not in period_info_list:
                        period_info_list.append(period_info)

    return period_info_list

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

MARKING_START_COL = 7
def parse_subjects(path: str) -> list[SubjectInfo]:
    board = get_board(path)
    data = template_subject.convolute(board)
    subject_info_list = []
    for _, contents in data.items():
        row_contents = contents[0]
        subject_data = {}
        for i, type_content in enumerate(row_contents):
            type = type_content[0]
            content = type_content[1]

            if type == 'subject':
                subject_data['subject'] = content
                continue

            if type == 'subject_type':
                subject_data['type'] = content
                continue

            if type == 'marking':
                if not content:
                    continue

                if subject_data.get('semester') is not None:
                    raise Exception('multiple semester checked')

                subject_data['semester'] = SEMESTER[i - MARKING_START_COL]

        subject_info_list.append(SubjectInfo(
            subject=subject_data['subject'],
            semester=subject_data.get('semester', -1),
            type=subject_data['type'],
        ))

    return subject_info_list

CELL_LENGTH = 3
DAY_START_COL = 1
TIMETABLE_START_COL = 2
BACK_TO_BACK_CLASS_ALIAS = ('│', 'BACK_TO_BACK')
CLASS_MARKER = 'CLASS'
def parse_common_timetable(
        path: str,
        alias: dict[str, str], # Subject name alias
) -> dict[tuple[int, int], TimetableInfo]: # (grade, class): info
    board = get_board(path)
    board_data = template_timetable.convolute(board)
    alias[BACK_TO_BACK_CLASS_ALIAS[0]] = BACK_TO_BACK_CLASS_ALIAS[1]
    timetable = {}
    for _, contents in board_data.items():
        grade, clazz, = (-1, -1)
        period_infos = {}
        for i, contents_row in enumerate(contents):
            for j, type_content in enumerate(contents_row):
                type = type_content[0]
                content = type_content[1]

                if type == 'skipped' or type == 'day':
                    continue

                if type == 'section':
                    grade = int(content[0])
                    clazz = int(content[1])
                    continue

                period = (i - TIMETABLE_START_COL) // CELL_LENGTH
                day = j - DAY_START_COL
                key = (day, period)

                if key not in period_infos:
                    period_infos[key] = {}

                if type == 'subject':
                    if content not in alias:
                        print('skipped: ' + str(content))
                        continue

                    subject = alias[content]
                    period_infos[(day, period)]['subject'] = subject

                if type == 'teacher':
                    period_infos[(day, period)]['teacher'] = content

                if type == 'room':
                    if not content:
                        content = CLASS_MARKER

                    period_infos[(day, period)]['room'] = content

        lecture_data = []
        period_data = []
        for key, data in period_infos.items():
            if 'subject' not in data:
                continue

            subject = data['subject']
            teacher = data['teacher']
            room = data['room'] if data['room'] != CLASS_MARKER else f'{grade}-{clazz}교실'

            if subject == BACK_TO_BACK_CLASS_ALIAS[1]:
                new_data = period_infos[(key[0], key[1] - 1)]

                subject = new_data['subject']
                teacher = new_data['teacher']
                room = new_data['room'] if new_data['room'] != CLASS_MARKER else f'{grade}-{clazz}교실'


            lecture_data.append(LectureInfo(
                subject=subject,
                teacher=teacher,
                room=room
            ))
            period_data.append(PeriodInfo(
                subject=subject,
                teacher=teacher,
                division=clazz,
                day=key[0],
                period=key[1]
            ))

        timetable[(grade, clazz)] = TimetableInfo(
            lectures=lecture_data,
            periods=period_data
        )

    return timetable

def parse_student_list(
        path: str
) -> list[StudentInfo]:
    board = get_board(path)
    board_data = template_student.convolute(board)
    student_info_list = []
    for _, contents in board_data.items():
        row_content = contents[0]
        student_info = {}
        for type_content in row_content:
            type = type_content[0]
            content = type_content[1]

            if type == 'name':
                student_info['name'] = content

            if type == 'student_number':
                grade, clazz, number =  content
                student_info['grade'] = grade
                student_info['clazz'] = clazz
                student_info['number'] = number

        student_info_list.append(StudentInfo(
            student_info['name'],
            get_generation(student_info['grade']),
            student_info['clazz'],
            student_info['number']
        ))

    return student_info_list