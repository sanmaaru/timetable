from sqlalchemy import select, or_, case
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, contains_eager
from ulid import ULID

from app.auth.exceptions import UnknownUserError
from app.auth.model import User, IdentifyToken, UserInfo


async def query_user(session: AsyncSession, user_id: ULID):
    stmt = select(User).where(User.user_id == user_id)
    user = (await session.execute(stmt)).scalars().one_or_none()

    if user is None:
        raise UnknownUserError('Cannot find user', payload={'user_id': user_id})

    return user

async def query_user_infos(session, role=None, search=None):
    stmt = (select(UserInfo)
            .outerjoin(UserInfo.user)
            .options(contains_eager(UserInfo.user)))

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

async def service_delete_user(session: AsyncSession, user_id: ULID):
    # 유저 삭제
    stmt = (select(User)
        .where(User.user_id == user_id)
        .options(
            joinedload(User.user_info)
        ))
    user = (await session.execute(stmt)).scalars().one_or_none()
    if user is None:
        raise UnknownUserError('Cannot find user', payload={'user_id': user_id})

    user_info = user.user_info
    await session.delete(user)

    # ID Token 생성
    identify_token = IdentifyToken(user_info_id=user_info.user_info_id)
    session.add(identify_token)