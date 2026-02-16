import ulid
from sqlalchemy import ForeignKey, String, SmallInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base, ULID, generate_ulid


class Lecture(Base):
    __tablename__ = 'lectures'

    lecture_id: Mapped[ulid.ULID] = mapped_column(ULID(), primary_key=True, default=generate_ulid)
    subject_id: Mapped[ulid.ULID] = mapped_column(ULID(), ForeignKey('subjects.subject_id'), nullable=False)
    teacher_info_id: Mapped[ulid.ULID] = mapped_column(ULID(), ForeignKey('user_infos.user_info_id'))
    room: Mapped[str] = mapped_column(String(255), nullable=True)

    subject = relationship('Subject', back_populates='lectures')
    teacher_info = relationship('UserInfo', back_populates='taught_lectures')
    classes = relationship(
        'Class', back_populates='lecture', cascade='all, delete-orphan'
    )


class Class(Base):
    __tablename__ = 'classes'

    class_id: Mapped[ulid.ULID] = mapped_column(ULID(), primary_key=True, default=generate_ulid)
    division: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    lecture_id: Mapped[ulid.ULID] = mapped_column(ULID(), ForeignKey('lectures.lecture_id'), nullable=False)

    lecture = relationship('Lecture', back_populates='classes')

    periods = relationship('Period', back_populates='clazz', cascade='all, delete-orphan')
    enrollments = relationship('Enrollment', back_populates='clazz', cascade='all, delete-orphan')
    classmates = relationship('UserInfo', secondary='enrollments', back_populates='classes',
                                 overlaps='enrollments, clazz')


class Subject(Base):
    __tablename__ = 'subjects'

    subject_id: Mapped[ulid.ULID] = mapped_column(ULID(), primary_key=True, default=generate_ulid)
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)

    lectures = relationship(
        'Lecture', back_populates='subject', cascade='all, delete-orphan'
    )


class Enrollment(Base):
    __tablename__ = 'enrollments'

    class_id: Mapped[ulid.ULID] = mapped_column(ULID(), ForeignKey('classes.class_id'), primary_key=True)
    user_info_id: Mapped[ulid.ULID] = mapped_column(ULID(), ForeignKey('user_infos.user_info_id'), primary_key=True,
                                                    nullable=False)

    clazz = relationship('Class', back_populates='enrollments')
    user_info = relationship('UserInfo', back_populates='enrollments')


class Period(Base):
    DAY = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']

    __tablename__ = 'periods'

    class_id: Mapped[ulid.ULID] = mapped_column(ULID(), ForeignKey('classes.class_id'), primary_key=True)
    period: Mapped[int] = mapped_column(SmallInteger, primary_key=True)
    day: Mapped[int] = mapped_column(SmallInteger, primary_key=True)

    clazz = relationship("Class", back_populates='periods')