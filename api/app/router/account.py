from fastapi import APIRouter
from fastapi.params import Depends, Path
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.crud.auth import crud_user, crud_user_info
from app.model.auth import User
from app.schema.auth import UserSchema
from app.core.database import conn
from app.core.dependencies import get_current_user, get_current_semester, get_current_user_with_info
from app.core.response import BaseResponse, create_response, SuccessResponse, MetaSchema
from app.core.types import ULIDModel
from app.model.timetable import Semester

router = APIRouter(prefix='/account', tags=['Account'])

@router.get('/', response_model=BaseResponse[UserSchema])
async def get_current_account(
    user: User = Depends(get_current_user_with_info),
):
    return create_response(user, user.user_id)


@router.delete('/', status_code=status.HTTP_202_ACCEPTED)
async def delete_account(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(conn),
):
    await crud_user.delete(session, condition=[User.user_id == user.user_id])
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
    semester: Semester = Depends(get_current_semester),
    session: AsyncSession = Depends(conn),
):
    queried_user = crud_user.query(session, condition=[User.user_id == user_id])
    queried_user_info = crud_user_info.query_by_semester(
        semester.semester_id, session, condition=[queried_user.identity_id]
    )
    setattr(queried_user, 'user_info', queried_user_info)

    return create_response(queried_user, user.user_id)
