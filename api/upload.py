from sqlalchemy.orm.session import Session
from database import User, Class, Subject, Lecture, Period, Enrollment
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
        return not content or content == 'nan'

    def interpret(self, content) -> None:
        return None
    
    def name(self) -> str:
        return "empty"

class SubjectCell(Cell[str]):

    __type__ = 'subject'

    def match(self, content: str) -> bool:
        return not content.isspace()
    
    def interpret(self, content: str) -> str:
        return content
    
    def name(self) -> str:
        return SubjectCell.__type__

class TeacherCell(Cell[str]):

    __type__ = 'teacher'

    def match(self, content: str) -> bool:
        return not content.isspace()
    
    def interpret(self, content: str) -> str:
        return content
    
    def name(self) -> str:
        return TeacherCell.__type__

class RoomCell(Cell[str]):

    __type__ = 'room'

    def match(self, content: str) -> bool:
        return not content.isspace()
    
    def interpret(self, content: str) -> str:
        return content
    
    def name(self) -> str:
        return RoomCell.__type__

class PeriodCell(Cell[list[tuple[int, list[int]]]]):

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
        
        

    def interpret(self, content: str) -> list[tuple[int, list[int]]]:
        contents = content.split("\n")
        result = []
        for content in contents:
            divided = content[:-1].split("(")
            division = int(divided[1].replace("분반", ""))
            periods = list(map(int, divided[0].split(",")))
            result.append((division, periods))
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
        print(h, self.height,w, self.width, h < self.height, w < self.width)
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

template_teacher = Template([[TEACHER, PERIOD, PERIOD, PERIOD, PERIOD, PERIOD]])

## ===== Upload Logic =====
def get_board(path):
    df = pd.read_excel(path)
    board = df.to_numpy()

    return board

def organize(stampped: list[list], allow_none=False):
    organized = {}
    for line in stampped:
        for type, content in line:
            if type == 'empty':
                continue

            if not allow_none and (not content or content == 'nan'):
                continue

            temp = organized.get(type, [])
            temp.append(content)
            organized[type] = temp

    for k, v in organized.items():
        if len(v) == 1:
            organized[k] = v[0]

    return organized


def upload_students(board, session: Session):
    data = template.convolute(board)
    for table in data.values():
        content = organize(table)

        stdinfo = content['student']
        grade, clazz, number, name = stdinfo[0], stdinfo[1], stdinfo[2], stdinfo[3]
        classes = content['class']

        student = session.query(User).filter(
            User.grade == grade,
            User.clazz == clazz, 
            User.number == number, 
            User.name == name).one_or_none()
        if student == None:
            raise ValueError('Cannot find student: ' + name)
        

        for lecture, division in classes:
            clazz = session.query(Class).filter(Class.division == division).all()
            clazz = next(filter(lambda x: x.lecture.subject.name == lecture, clazz))
            enrollment = Enrollment(class_id=clazz.class_id, user_id=student.user_id)
            session.add(enrollment)
        
        session.commit()
            

        
        

def upload_lecture(board, session: Session):
    data = template_room.convolute(board)
    for table in data.values():
        content = organize(table)
        subject_name = content['subject']
        
        # create subject
        subject = Subject(name=subject_name)
        session.add(subject)
        session.commit()
        session.refresh(subject)

        # create lecture
        for teachers, room in zip(content['teacher'], content['room']):
            teacher_name = teachers.split(",")[0].strip()
            teacher = session.query(User).filter(User.name == teacher_name, User.role == 'tch').one_or_none()
            if teacher == None:
                print('Cannot find teacher: ' + teacher_name)
                continue
            
            lecture = Lecture(subject_id=subject.subject_id, teacher_id=teacher.user_id, room=room)
            session.add(lecture)
            session.commit()
            

def upload_class(board, session: Session):
    data = template_teacher.convolute(board)
    for table in data.values():
        content = organize(table, allow_none=True)
        teacher_name = content['teacher'].split(',')[0].strip()
        periods = content['period']

        # Lecture 가져오기
        teacher = session.query(User).filter(User.name == teacher_name, User.role == 'tch').one_or_none()
        if teacher == None:
            raise ValueError('Cannot find teacher: ' + teacher_name)
        
        lecture = session.query(Lecture).filter(Lecture.teacher_id == teacher.user_id).one_or_none()
        if lecture == None:
            raise ValueError('cannot find lecture taught by ' + teacher.name)


        # Class & Period 생성하기
        for day, period in enumerate(periods):
            if period == None:
                continue

            for division, period in period:
                for period in period:
                    clazz = session.query(Class).where(Class.lecture_id == lecture.lecture_id,
                                                       Class.division == division).one_or_none()
                    if clazz == None:
                        clazz = Class(lecture_id=lecture.lecture_id, division=division)
                        session.add(clazz)
                        session.commit()
                        session.refresh(clazz)
                    
                    period = Period(class_id=clazz.class_id, period=period, day=day+1)
                    session.add(period)
                    session.commit()
            



if __name__ == '__main__':
    board = get_board('2025 강의실 2.xlsx')
    # print(board)
    # print(template_teacher.stamp(board, 1, 1))
    for idx, data in template_room.convolute(board).items():
        content = organize(data, allow_none=False)
        print(content)