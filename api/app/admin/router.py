from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.admin.crud import query_user_infos, query_subjects
from app.auth.model import User
from app.auth.schemas import UserSchema
from app.core.database import conn
from app.core.dependencies import get_current_admin_user
from app.core.response import BaseResponse, create_response
from app.core.types import get_role
from app.timetable.schemas import SubjectSchema, PeriodSchema

router = APIRouter(prefix='/admin', tags=['Admin'])

@router.get('/userInfo', response_model=BaseResponse[List[UserSchema]])
async def get_user_infos(
        role: str | None = None,
        search: str | None = None,
        user: User = Depends(get_current_admin_user),
        session: AsyncSession = Depends(conn),
):
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


@router.get('/subject', response_model=BaseResponse[List[SubjectSchema]])
async def get_subjects(
        search: str | None = None,
        user: User = Depends(get_current_admin_user),
        session: AsyncSession = Depends(conn),
):
    subjects = [SubjectSchema.model_validate(subject) for subject in await query_subjects(session, search)]
    return create_response(subjects, user.user_id)


@router.get('/period', response_model=BaseResponse[List[PeriodSchema]])
async def get_periods(
        lecture_id: str
):
    pass