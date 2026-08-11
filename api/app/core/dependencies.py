import structlog
from fastapi import Header, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.account.crud import query_user_info
from app.auth.crud import decode_access
from app.auth.exceptions import AuthorizationError, NoPermissionError
from app.auth.model import User
from app.core.database import conn
from app.core.types import Role
from app.timetable.exceptions import SemesterNotSelectedError
from app.timetable.model import Semester

logger = structlog.get_logger()

async def get_current_semester(
        session: AsyncSession = Depends(conn)
) -> Semester:
    stmt = select(Semester).where(Semester.is_current == True)
    current_semester = (await session.execute(stmt)).scalars().one_or_none()

    if current_semester is None:
        raise SemesterNotSelectedError(message="Semester not selected")

    return current_semester


async def get_current_user(
        auth: str = Header(default=None, alias="Authorization"),
        session: AsyncSession = Depends(conn)
) -> User:
    if auth is None:
        raise AuthorizationError(
            status_code=status.HTTP_401_UNAUTHORIZED,
            message='Authorization header missing'
        )

    scheme, _, token = auth.partition(" ")
    if scheme.lower() != 'bearer':
        raise AuthorizationError(message="Infelicitous token type")

    jwt = decode_access(token)
    user_id = jwt.sub
    stmt = select(User).filter(User.user_id == user_id)

    user = (await session.execute(stmt)).scalars().one_or_none()

    if user is None:
        raise AuthorizationError(message="Invalid User")

    return user


async def get_current_user_with_info(
        user: User = Depends(get_current_user),
        semester: Semester = Depends(get_current_semester),
        session: AsyncSession = Depends(conn)
) -> User:
    # Query and inject user info to user
    user_info = await query_user_info(user.identity_id, semester.semester_id, session)
    setattr(user, 'user_info', user_info)

    return user


async def get_current_admin_user(
        current_user = Depends(get_current_user_with_info),
) -> User:
    if Role.ADMINISTRATOR != current_user.user_info.role:
        raise NoPermissionError(message="User is not administrator")

    return current_user
