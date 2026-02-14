from fastapi import Header, Depends, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.auth import JWT
from app.auth.exceptions import AuthorizationError
from app.core.database import conn
from app.auth.model import User


def get_current_user(
        auth: str = Header(default=None, alias="Authorization"),
        session: Session = Depends(conn)
):
    if auth is None:
        raise AuthorizationError(
            status_code=status.HTTP_401_UNAUTHORIZED,
            message='Authorization header missing'
        )

    scheme, _, token = auth.partition(" ")
    if scheme.lower() != 'bearer' or scheme is None:
        raise AuthorizationError(message="Infelicitous token type")

    jwt = JWT.decode(token)
    if jwt is None or not jwt.verify():
        raise AuthorizationError(message="Invalid authorization token")

    user_id = jwt.user_id
    stmt = select(User).filter(User.user_id == user_id)
    user = session.execute(stmt).scalars().one_or_none()

    if user is None:
        raise AuthorizationError(message="Invalid User")

    return user