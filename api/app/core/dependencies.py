import structlog
from fastapi import Header, Depends, status
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import configs
from app.crud.auth import crud_user_info
from app.crud.timetable import crud_semester
from app.exceptions.auth import AuthorizationError, NoPermissionError
from app.model.auth import User
from app.core.database import conn
from app.core.types import Role
from app.exceptions.timetable import SemesterNotSelectedError
from app.model.timetable import Semester
from app.schema.auth import TokenPayload

logger = structlog.get_logger()

async def get_current_semester(
        session: AsyncSession = Depends(conn)
) -> Semester:
    current_semester = await crud_semester.query(session, condition=[Semester.is_current == True])

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

    # Decode jwt
    try:
        payload = jwt.decode(token, configs.JWT_SECRET, algorithms=[configs.JWT_ALGORITHM])
        decoded = TokenPayload(**payload)

    except JWTError:
        raise AuthorizationError('Could not validate credentials')

    if decoded.sub is None:
        raise AuthorizationError('Token missing subject (user_id)')

    user_id = decoded.sub
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
    user_info = await crud_user_info.query_by_identity_id(user.identity_id, semester.semester_id, session)
    setattr(user, 'user_info', user_info)

    return user


async def get_current_admin_user(
        current_user = Depends(get_current_user_with_info),
) -> User:
    if Role.ADMINISTRATOR != current_user.user_info.role:
        raise NoPermissionError(message="User is not administrator")

    return current_user
