from typing import List

from fastapi import APIRouter
from fastapi.params import Depends, Path, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.annotation import Annotated
from starlette import status

from app.account.crud import query_user, service_delete_user, query_user_infos
from app.auth.crud import Role
from app.auth.exceptions import NoPermissionError
from app.auth.model import User
from app.auth.schemas import UserSchema, UserInfoSchema
from app.core.database import conn
from app.core.dependencies import get_current_user
from app.core.response import BaseResponse, create_response, SuccessResponse, MetaSchema
from app.core.types import ULIDModel, get_role

router = APIRouter(prefix='/account', tags=['Account'])

@router.get('/', response_model=BaseResponse[UserSchema])
async def get_current_account(
    user: User = Depends(get_current_user),
):
    return create_response(user, user.user_id)

@router.delete('/', status_code=status.HTTP_202_ACCEPTED)
async def delete_account(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(conn),
):
    await service_delete_user(session, user.user_id)
    await session.commit()
    return SuccessResponse(
        meta = MetaSchema(
            user_id = 'Not Exist',
            status = status.HTTP_202_ACCEPTED,
        )
    )

@router.get('/userInfo', response_model=BaseResponse[List[UserSchema]])
async def get_user_infos(
        role: str | None = None,
        search: str | None = None,
        user: User = Depends(get_current_user),
        session: AsyncSession = Depends(conn),
):
    if user.user_info.role < Role.MANAGER:
        raise NoPermissionError('No permission')

    user_infos = await query_user_infos(
        session,
        role=get_role(role),
        search=search
    )
    user_profiles = []
    for user_info in user_infos:
        u = user_info.user
        if u is None:
            mock_user = UserSchema(
                user_id=None,
                email=None,
                username=None,
                user_info=user_info
            )
            user_profiles.append(mock_user)
            continue

        user_profiles.append(u)

    return create_response(user_profiles, user.user_id)

@router.get('/{user_id}', response_model=BaseResponse[UserSchema])
async def get_account(
    user: User = Depends(get_current_user),
    user_id: ULIDModel = Path(description='user id you want to query'),
    session: AsyncSession = Depends(conn),
):
    queried_user = query_user(session, user_id)
    return create_response(queried_user, user.user_id)
