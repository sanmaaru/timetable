from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload
from ulid.ulid import ULID

from app.auth.model import User, UserInfo
from app.timetable.exceptions import UnknownClassError
from app.timetable.model import Class, Lecture
from app.timetable.schemas import TimetableSchema


async def query_timetable(user: User, session: AsyncSession):
    stmt = (
        select(UserInfo)
        .options(
            selectinload(UserInfo.classes).options(
                selectinload(Class.periods),
                selectinload(Class.classmates),
                joinedload(Class.lecture).joinedload(Lecture.subject),
                joinedload(Class.lecture).joinedload(Lecture.teacher_info)
            )
        )
        .where(UserInfo.user_info_id == user.user_info_id)
    )
    result = await session.execute(stmt)
    user_info = result.scalar_one()

    return TimetableSchema(
        username=user.username,
        name=user_info.name,
        timetable=user_info.classes
    )

async def query_class(class_id: ULID, session: AsyncSession):
    stmt = select(Class).options(
        selectinload(Class.classmates),
        selectinload(Class.periods),
        joinedload(Class.lecture).joinedload(Lecture.subject),
        joinedload(Class.lecture).joinedload(Lecture.teacher_info)
    ).where(Class.class_id == class_id)

    result = (await session.execute(stmt)).scalars().one_or_none()
    if result is None:
        raise UnknownClassError('Cannot find class for ' + str(class_id))

    return result