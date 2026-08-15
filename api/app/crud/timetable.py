from typing import Type

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import contains_eager, joinedload, selectinload

from app.core.database import ULID
from app.crud.base import CRUDSemesterMixin, CRUDBase, ModelType
from app.model.timetable import Lecture, Subject, Period, Enrollment, Semester


class CRUDSubject(CRUDSemesterMixin[Subject]):

    def __init__(self):
        super().__init__(Subject)


    async def search_by_semester(
            self,
            semester_id: ULID,
            session: AsyncSession,
            search: str | None = None
    ):
        stmt = (select(
            Subject.subject_id,
            Subject.name,
            func.count(Lecture.lecture_id).label('lecture_count')
        ).outerjoin(Subject.lectures)
                .options(contains_eager(Subject.lectures))
                .group_by(Subject.subject_id)
                .order_by(Subject.name.asc())
                .where(Subject.semester_id == semester_id))

        if search:
            pattern = f'%{search}%'
            stmt = stmt.where(Subject.name.ilike(pattern))

        return (await session.scalars(stmt)).all()


class CRUDLecture(CRUDSemesterMixin[Lecture]):

    def __init__(self):
        super().__init__(Lecture)


    async def list_with_relation(
            self,
            semester_id: ULID,
            session: AsyncSession,
            condition: list | None = None,
            option: list | None = None
    ):
        stmt = select(self.model).join(self.model.subject).join(self.model.teacher_info)
        conditions = list(condition) if condition else []
        conditions.append(self.model.semester_id == semester_id)
        stmt = stmt.where(*conditions)

        options = list(option) if option else []
        options += [
            contains_eager(Lecture.teacher_info),
            contains_eager(Lecture.subject)
        ]
        stmt = stmt.options(*options)

        return (await session.scalars(stmt)).all()


    async def query_with_detail(
            self,
            semester_id: ULID,
            session: AsyncSession,
            condition: list | None = None,
            option: list | None = None
    ):
        options = list(option) if option else []
        options += [
            joinedload(Lecture.subject),
            joinedload(Lecture.teacher_info),
            selectinload(Lecture.classmates),
            selectinload(Lecture.periods)
        ]

        return super().query_by_semester(semester_id, session, condition, options)


class CRUDPeriod(CRUDSemesterMixin[Period]):

    def __init__(self):
        super().__init__(Period)


class CRUDEnrollment(CRUDSemesterMixin[Enrollment]):

    def __init__(self):
        super().__init__(Enrollment)


class CRUDSemester(CRUDBase[Semester]):

    def __init__(self):
        super().__init__(Semester)


crud_subject = CRUDSubject()
crud_lecture = CRUDLecture()
crud_period = CRUDPeriod()
crud_enrollment = CRUDEnrollment()
crud_semester = CRUDSemester()