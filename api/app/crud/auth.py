from sqlalchemy import select, or_, case
from sqlalchemy.ext.asyncio import AsyncSession
from ulid import ULID

from app.crud.base import CRUDSemesterMixin, CRUDBase
from app.model.auth import User, UserInfo, IdentifyToken, RefreshToken


class CRUDUser(CRUDBase[User]):

    def __init__(self):
        super().__init__(User)


class CRUDUserInfo(CRUDSemesterMixin[UserInfo]):

    def __init__(self):
        super().__init__(UserInfo)

    async def search_by_semester(
            self,
            semester_id: ULID,
            session :AsyncSession,
            search: str | None = None,
            role: int | None = None
    ):
        stmt = select(self.model)

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

        return await session.scalars(stmt)


    async def query_by_identity_id(
            self,
            identity_id: str,
            semester_id: ULID,
            session : AsyncSession,
    ):
        return await self.query_by_semester(
            semester_id=semester_id,
            session=session,
            condition=[
                UserInfo.identity_id == identity_id
            ]
        )


class CRUDIdentifyToken(CRUDBase[IdentifyToken]):

    def __init__(self):
        super().__init__(IdentifyToken)


class CRUDRefreshToken(CRUDBase[RefreshToken]):

    def __init__(self, ):
        super().__init__(RefreshToken)


crud_user = CRUDUser()
crud_user_info = CRUDUserInfo()
crud_identify_token = CRUDIdentifyToken()
crud_refresh_token = CRUDRefreshToken()