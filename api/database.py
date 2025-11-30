from sqlalchemy import (
    Column, Float, ForeignKey, SmallInteger, String, Integer, create_engine
)
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from dotenv import load_dotenv
from datetime import datetime
from util import get_grade
import os, uuid

load_dotenv('../.env')

url = os.getenv('CONNECTION')
assert url != None
engine = create_engine(url, pool_pre_ping=True)

def gen_uuid() -> str:
    return str(uuid.uuid4())

## Tables
Base = declarative_base()

# ===== Basic =====
class Lecture(Base):

    __tablename__ = 'lectures'

    lecture_id = Column(String(36), primary_key=True, default=gen_uuid)
    subject_id = Column(String(36), ForeignKey('subjects.subject_id'), nullable=False)
    teacher_info_id = Column(String(36), ForeignKey('users_info.user_info_id'))
    room = Column(String(255), nullable=True)

    subject = relationship('Subject', back_populates='lectures')
    teacher_info = relationship('UserInfo', back_populates='taught_lectures')
    classes = relationship(
        'Class', back_populates='lecture', cascade='all, delete-orphan'
    )


class Class(Base):

    __tablename__ = 'classes'

    class_id = Column(String(36), primary_key=True, default=gen_uuid)
    division = Column(SmallInteger, nullable=False)
    lecture_id = Column(String(36), ForeignKey('lectures.lecture_id'), nullable=False)

    lecture = relationship('Lecture', back_populates='classes')
    
    periods = relationship('Period', back_populates='clazz', cascade='all, delete-orphan')
    enrollments = relationship('Enrollment', back_populates='clazz', cascade='all, delete-orphan')
    students_info = relationship('UserInfo', secondary='enrollments', back_populates='classes')



class Subject(Base):

    __tablename__ = 'subjects'

    subject_id = Column(String(36), primary_key=True, default=gen_uuid)
    name = Column(String(255), nullable=False, unique=True)

    lectures = relationship(
        'Lecture', back_populates='subject', cascade='all, delete-orphan'
    )

class Enrollment(Base):
    
    __tablename__ = 'enrollments'

    class_id = Column(String(36), ForeignKey('classes.class_id'), primary_key=True)
    user_info_id = Column(String(36), ForeignKey('users_info.user_info_id'), primary_key=True, nullable=False)

    clazz = relationship('Class', back_populates='enrollments')
    user_info = relationship('UserInfo', back_populates='enrollments')

class Period(Base):

    DAY = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']

    __tablename__ = 'periods'

    class_id = Column(String(36), ForeignKey('classes.class_id'), primary_key=True)
    period = Column(SmallInteger, primary_key=True)
    day = Column(SmallInteger, primary_key=True)

    clazz = relationship("Class", back_populates='periods')

# ===== Auth =====
class User(Base):

    __tablename__ = 'users'

    user_id = Column(String(36), primary_key=True)
    id = Column(String(20), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    user_info_id = Column(String(36), ForeignKey('users_info.user_info_id'), nullable=False, unique=True)

    user_info = relationship('UserInfo', uselist=False, back_populates='user')

    def __repr__(self):
        return 'user { user_id: {' + str(self.user_id) + '}, id: {' + str(self.id) + '}, password: {' + str(self.password) + '} }'
    
class UserInfo(Base):

    __tablename__ = 'users_info'

    user_info_id = Column(String(36), primary_key=True)
    name = Column(String(255), nullable=False)
    role = Column(String(3), nullable=False) # role: stu -> student / tch -> teacher / adm -> administrator
    clazz = Column(SmallInteger, nullable=True)
    number = Column(SmallInteger, nullable=True)
    generation = Column(SmallInteger, nullable=True)
    credit = Column(Integer, nullable=True)
    
    taught_lectures = relationship('Lecture', back_populates='teacher_info')
    enrollments = relationship('Enrollment', back_populates='user_info', cascade='all, delete-orphan')
    classes = relationship('Class', secondary='enrollments', back_populates='students_info')

    user = relationship('User', uselist=False, back_populates='user_info')

    @property
    def grade(self):
        return get_grade(self.generation)
    
class RefreshToken(Base):

    __tablename__ = 'refresh_tokens'

    token_id = Column(String(36), primary_key=True)
    issuer = Column(String(255), nullable=False)
    issued_at = Column(Float(), nullable=False)
    expired_at = Column(Float(), nullable=False)
    jwt_signature = Column(String(255), nullable=False)

class IdentifyToken(Base):

    __tablename__ = 'identify_tokens'

    token_id = Column(String(8), primary_key=True)
    user_info_id = Column(String(36), ForeignKey('users_info.user_info_id'), nullable=False, unique=True)

    user_info = relationship('UserInfo', uselist=False)


def init_db():
    Base.metadata.create_all(engine)

LocalSession = sessionmaker(bind=engine)

def conn():
    session = LocalSession()
    try:
        yield session
    finally:
        session.close()