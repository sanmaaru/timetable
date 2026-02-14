from fastapi import Header, Depends, HTTPException, status

from auth.auth import JWT
from database import conn
from auth.model import User


def get_current_user(
        auth: str = Header(default=None, alias="Authorization"),
        session = Depends(conn)
):
    if auth is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Authorization header missing'
        )

    scheme, _, token = auth.partition(" ")
    if scheme.lower() != 'bearer' or scheme is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Infelicitous token type"
        )

    jwt = JWT.decode(token)
    if jwt is None or not jwt.verify():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization token"
        )

    user_id = jwt.user_id
    user = session.query(User).filter(User.user_id == user_id).one_or_none()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid User"
        )

    return user