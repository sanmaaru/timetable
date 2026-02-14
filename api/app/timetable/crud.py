from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload

from app.auth.model import User, UserInfo
from app.timetable.model import Class, Lecture
from app.timetable.schemas import TimetableSchema


async def query_timetable(user: User, session: AsyncSession):
    stmt = (
        select(UserInfo)
        .options(
            selectinload(UserInfo.classes).options(
                selectinload(Class.periods),
                joinedload(Class.lecture).joinedload(Lecture.subject),
                joinedload(Class.lecture).joinedload(Lecture.teacher_info)
            )
        )
        .where(UserInfo.user_id == user.user_id)
    )
    result = await session.execute(stmt)
    user_info = result.scalar_one()

    # 2. 스키마에 데이터 주입
    # Pydantic이 user_info.classes를 리스트로 순회하며
    # TimetableItemSchema로 자동 변환합니다.
    return TimetableSchema(
        username=user.username,
        name=user_info.name,
        timetable=user_info.classes
    )