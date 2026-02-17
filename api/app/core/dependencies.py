from fastapi import Header, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.auth.crud import decode_access
from app.auth.exceptions import AuthorizationError
from app.auth.model import User
from app.core.database import conn


async def get_current_user(
        auth: str = Header(default=None, alias="Authorization"),
        session: AsyncSession = Depends(conn)
):
    if auth is None:
        raise AuthorizationError(
            status_code=status.HTTP_401_UNAUTHORIZED,
            message='Authorization header missing'
        )

    scheme, _, token = auth.partition(" ")
    if scheme.lower() != 'bearer' or scheme is None:
        raise AuthorizationError(message="Infelicitous token type")

    jwt = decode_access(token)
    user_id = jwt.sub
    stmt = select(User).filter(User.user_id == user_id).options(
        joinedload(User.user_info)
    )
    user = (await session.execute(stmt)).scalars().one_or_none()

    if user is None:
        raise AuthorizationError(message="Invalid User")

    return user