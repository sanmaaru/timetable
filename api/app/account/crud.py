from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from ulid import ULID

from app.auth.exceptions import UnknownUserError
from app.auth.model import User, IdentifyToken


async def query_user(user_id: ULID, session: AsyncSession):
    stmt = select(User).where(User.user_id == user_id)
    user = (await session.execute(stmt)).scalars().one_or_none()

    if user is None:
        raise UnknownUserError('Cannot find user', payload={'user_id': user_id})

    return user

async def service_delete_user(user_id: ULID, session: AsyncSession):
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