from fastapi import APIRouter
from fastapi.params import Depends, Path
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.account.crud import query_user, service_delete_user
from app.auth.model import User
from app.auth.schemas import UserSchema
from app.core.database import conn
from app.core.dependencies import get_current_user
from app.core.response import BaseResponse, create_response, SuccessResponse, MetaSchema
from app.core.types import ULIDModel

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
    await service_delete_user(user.user_id, session)
    await session.commit()
    return SuccessResponse(
        meta = MetaSchema(
            user_id = 'Not Exist',
            status = status.HTTP_202_ACCEPTED,
        )
    )


@router.get('/{user_id}', response_model=BaseResponse[UserSchema])
async def get_account(
    user: User = Depends(get_current_user),
    user_id: ULIDModel = Path(description='user id you want to query'),
    session: AsyncSession = Depends(conn),
):
    queried_user = query_user(user_id=user_id, session=session)
    return create_response(queried_user, user.user_id)