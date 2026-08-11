import ulid
from sqlalchemy import select, or_, case
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, contains_eager
from sqlalchemy import update
from ulid import ULID

from app.auth.exceptions import UnknownUserError, UnknownUserInfoError
from app.auth.model import User, IdentifyToken, UserInfo


async def query_user(user_id: ULID, session: AsyncSession):
    stmt = select(User).where(User.user_id == user_id)
    user = (await session.execute(stmt)).scalars().one_or_none()

    if user is None:
        raise UnknownUserError('Cannot find user', payload={'user_id': user_id})

    return user


async def query_user_info(identity_id: str, semester_id: ulid.ULID, session: AsyncSession):
    stmt = (select(UserInfo)
            .where(
                UserInfo.identity_id == identity_id,
                UserInfo.semester_id == semester_id
            ))

    user_info = (await session.execute(stmt)).scalars().one_or_none()

    if user_info is None:
        raise UnknownUserInfoError(
            'Cannot find user info',
            payload={'identity_id': identity_id, 'semester_id': semester_id}
        )

    return user_info


async def service_delete_user(session: AsyncSession, user_id: ULID):
    # delete user
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

    # Reactivate identify token
    stmt = update(IdentifyToken).where(IdentifyToken.identity_id == user_info.identity_id).values(expired=False)
    await session.execute(stmt)