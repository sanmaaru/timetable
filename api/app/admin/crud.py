import ulid
from sqlalchemy import select, or_, case, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import contains_eager

from app.auth.model import UserInfo, User
from app.timetable.model import Subject, Lecture, Period
from app.timetable.schemas import SubjectSchema


async def query_user_infos(session: AsyncSession, role=None, search=None):
    stmt = (select(UserInfo))

    if role is not None:
        stmt = stmt.where(UserInfo.role == role)

    if search:
        pattern = f'%{search}%'
        stmt = stmt.where(
            or_(
                UserInfo.name.ilike(pattern),
                User.username.ilike(pattern),
                User.email.ilike(pattern)
            )
        )

        stmt = stmt.order_by(
            case(
                (UserInfo.name.ilike(pattern), 1),
                (User.username.ilike(pattern), 2),
                else_=3
            ),
            UserInfo.name.asc()
        )
    else:
        stmt = stmt.order_by(UserInfo.name.asc())

    user_infos = (await session.execute(stmt)).scalars().all()
    return user_infos


async def query_subjects(session: AsyncSession, search=None):
    stmt = (select(
                Subject.subject_id,
                Subject.name,
                func.count(Lecture.lecture_id).label('lecture_count')
            )
            .outerjoin(Subject.lectures)
            .options(contains_eager(Subject.lectures))
            .group_by(Subject.subject_id)
            .order_by(Subject.name.asc())
    )

    if search:
        pattern = f'%{search}%'
        stmt = stmt.where(Subject.name.ilike(pattern))

    subjects = (await session.scalars(stmt)).all()

    return subjects


async def query_lectures(session: AsyncSession, search=None):
    stmt = (

    )

async def query_periods(lecture_id: ulid.ULID, session: AsyncSession):
    stmt = select(Period).where(Period.lecture_id == lecture_id)
    periods = (await session.scalars(stmt)).unique().all()

    return periods