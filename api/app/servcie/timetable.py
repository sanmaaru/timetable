from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload

from app.core.database import ULID
from app.crud.auth import crud_user_info
from app.crud.timetable import crud_lecture
from app.exceptions.base import NotFoundError
from app.model.auth import UserInfo
from app.model.timetable import Semester, Lecture


class TimetableService:

    @staticmethod
    async def query_timetable(
            identity_id: str,
            semester: Semester,
            session: AsyncSession,
    ):
        user_info = await crud_user_info.query_by_identity_id(
            identity_id, semester.semester_id, session,
            option=[
                selectinload(UserInfo.lectures).options(
                    joinedload(Lecture.subject),
                    joinedload(Lecture.teacher_info),
                    selectinload(Lecture.periods),
                )
            ]
        )

        if not user_info:
            raise NotFoundError(f'Cannot find user {identity_id} in {semester.code}')

        return user_info.lectures, user_info.name


    @staticmethod
    async def query_classmates(
            lecture_id: ULID,
            semester: Semester,
            session: AsyncSession,
    ):
        lecture = await crud_lecture.query_by_semester(
            semester.semester_id, session,
            condition=[Lecture.lecture_id == lecture_id],
            option=[
                selectinload(Lecture.classmates)
            ]
        )

        if not lecture:
            raise NotFoundError(f'Cannot find lecture {lecture_id} in {semester.code}')

        return lecture.classmates
