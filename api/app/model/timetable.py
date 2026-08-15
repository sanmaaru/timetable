import ulid
from sqlalchemy import ForeignKey, String, SmallInteger, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship, declared_attr

from app.core.database import Base, ULID, generate_ulid

class Semester(Base):
    __tablename__ = 'semesters'

    semester_id: Mapped[ulid.ULID] = mapped_column(ULID(), primary_key=True, default=generate_ulid)
    code: Mapped[str] = mapped_column(String(32), unique=True, nullable=False)
    is_current: Mapped[bool] = mapped_column(default=False)


class SemesterMixin:
    semester_id: Mapped[ulid.ULID] = mapped_column(ULID(), ForeignKey('semesters.semester_id'), nullable=False)


class Lecture(Base, SemesterMixin):
    __tablename__ = 'lectures'

    lecture_id: Mapped[ulid.ULID] = mapped_column(ULID(), primary_key=True, default=generate_ulid)
    subject_id: Mapped[ulid.ULID] = mapped_column(ULID(), ForeignKey('subjects.subject_id'), nullable=False)
    teacher_info_id: Mapped[ulid.ULID] = mapped_column(ULID(), ForeignKey('user_infos.user_info_id'))
    room: Mapped[str] = mapped_column(String(255), nullable=True)
    division: Mapped[int] = mapped_column(SmallInteger, nullable=False)

    subject: Mapped['Subject'] = relationship('Subject', back_populates='lectures')
    teacher_info = relationship('UserInfo', back_populates='taught_lectures')
    periods: Mapped['Period'] = relationship('Period', back_populates='lecture', cascade='all, delete-orphan')
    enrollments: Mapped['Enrollment'] = relationship('Enrollment', back_populates='lecture', cascade='all, delete-orphan')
    classmates = relationship('UserInfo', secondary='enrollments', back_populates='lectures',
                              overlaps='enrollments, clazz')

    __table_args__ = (
        UniqueConstraint(
            "subject_id",
            "teacher_info_id",
            "division",
            "semester_id",
            name="unique_lecture_semester"
        ),
    )


class Subject(Base, SemesterMixin):
    __tablename__ = 'subjects'

    subject_id: Mapped[ulid.ULID] = mapped_column(ULID(), primary_key=True, default=generate_ulid)
    name: Mapped[str] = mapped_column(String(255), nullable=False)

    lectures = relationship(
        'Lecture', back_populates='subject', cascade='all, delete-orphan'
    )

    __table_args__ = (
        UniqueConstraint("name", "semester_id", name="unique_subject_semester"),
    )


class Enrollment(Base, SemesterMixin):
    __tablename__ = 'enrollments'

    enrollment_id: Mapped[ulid.ULID] = mapped_column(ULID(), primary_key=True, default=generate_ulid)
    lecture_id: Mapped[ulid.ULID] = mapped_column(ULID(), ForeignKey('lectures.lecture_id'), nullable=False)
    user_info_id: Mapped[ulid.ULID] = mapped_column(ULID(), ForeignKey('user_infos.user_info_id'), nullable=False)

    lecture: Mapped[Lecture] = relationship('Lecture', back_populates='enrollments')
    user_info = relationship('UserInfo', back_populates='enrollments')

    __table_args__ = (
        UniqueConstraint(
            'lecture_id',
            'user_info_id',
            'semester_id',
            name='unique_enrollment_semester'
        ),
    )


class Period(Base, SemesterMixin):
    DAY = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']

    __tablename__ = 'periods'

    period_id: Mapped[ulid.ULID] = mapped_column(ULID(), primary_key=True, default=generate_ulid)

    lecture_id: Mapped[ulid.ULID] = mapped_column(ULID(), ForeignKey('lectures.lecture_id'))
    period: Mapped[int] = mapped_column(SmallInteger)
    day: Mapped[int] = mapped_column(SmallInteger)

    lecture: Mapped[Lecture] = relationship("Lecture", back_populates='periods')

    __table_args__ = (
        UniqueConstraint(
            'lecture_id',
            'period',
            'day',
            'semester_id',
            name='unique_period_semester'
        ),
    )
