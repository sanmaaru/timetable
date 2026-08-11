from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload
from ulid.ulid import ULID

from app.auth.model import User, UserInfo
from app.core.config import Configs, configs
from app.timetable.exceptions import UnknownClassError
from app.timetable.model import Lecture, Semester
from app.timetable.schemas import TimetableSchema


async def query_timetable(user: User, session: AsyncSession):
    stmt = (
        select(UserInfo)
        .options(
            selectinload(UserInfo.lectures).options(
                selectinload(Lecture.periods),
                selectinload(Lecture.classmates),
                joinedload(Lecture.subject),
                joinedload(Lecture.teacher_info)
            )
        )
        .where(UserInfo.identity_id == user.identity_id)
    )
    result = await session.execute(stmt)
    user_info = result.scalar_one()

    return TimetableSchema(
        username=user.username,
        name=user_info.name,
        timetable=user_info.classes
    )


async def query_lecture(lecture_id: ULID, session: AsyncSession):
    stmt = select(Lecture).options(
        selectinload(Lecture.classmates),
        selectinload(Lecture.periods),
        joinedload(Lecture.subject),
        joinedload(Lecture.teacher_info)
    ).where(Lecture.lecture_id == lecture_id)

    result = (await session.execute(stmt)).scalars().one_or_none()
    if result is None:
        raise UnknownClassError('Cannot find lecture for ' + str(lecture_id))

    return result