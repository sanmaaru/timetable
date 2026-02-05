import binascii
import os
import uuid
from typing import Any

import ulid
from dotenv import load_dotenv
from sqlalchemy import (
    Column, ForeignKey, SmallInteger, String, create_engine, TypeDecorator, BINARY, LargeBinary
)
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

load_dotenv('../.env')

url = os.getenv('CONNECTION')
assert url is not None
engine = create_engine(url, pool_pre_ping=True)

def gen_uuid() -> str:
    return str(uuid.uuid4())

class ULID(TypeDecorator):

    impl = BINARY(16)
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return None

        if isinstance(value, str):
            value = ulid.from_str(value)

        return value.bytes

    def process_result_value(self, value, dialect):
        if value is None:
            return None

        return ulid.from_bytes(value)


def generate_ulid():
    return ulid.new()

class Hex(TypeDecorator):

    impl = LargeBinary
    cache_ok = True

    def __init__(self, length = None, **kwargs):
        if length is not None:
            length = (length + 1) // 2
            super().__init__(length=length, **kwargs)
        else:
            super().__init__(**kwargs)

    def process_bind_param(self, value: str, dialect) -> Any:
        if value is None:
            return None

        value = value.replace("#", "").replace('0x', '').strip()
        if len(value) % 2 != 0:
            value = '0' + value

        return binascii.unhexlify(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return None

        return binascii.hexlify(value).decode('utf-8')


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
    students_info = relationship('UserInfo', secondary='enrollments', back_populates='classes', overlaps='enrollments, clazz')



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

def init_db():
    Base.metadata.create_all(engine)

LocalSession = sessionmaker(bind=engine)

def conn():
    session = LocalSession()
    try:
        yield session
    finally:
        session.close()