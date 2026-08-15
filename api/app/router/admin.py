from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import conn
from app.core.dependencies import get_current_admin_user, get_current_semester
from app.core.response import BaseResponse, create_response
from app.core.types import get_role
from app.crud.auth import crud_user_info
from app.crud.timetable import crud_subject
from app.model.auth import User
from app.model.timetable import Semester
from app.schema.auth import UserSchema
from app.schema.timetable import SubjectSchema, LectureSchema

router = APIRouter(prefix='/admin', tags=['Admin'])

@router.get('/userInfo', response_model=BaseResponse[List[UserSchema]])
async def get_user_infos(
        role: str | None = None,
        search: str | None = None,
        user: User = Depends(get_current_admin_user),
        semester: Semester = Depends(get_current_semester),
        session: AsyncSession = Depends(conn),
):
    user_infos = crud_user_info.search_by_semester(
        semester.semester_id,
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
                user_info=user_info,
                identity_id = user_info.identity_id,
            )
            user_profiles.append(mock_user)
            continue

        user_profiles.append(u)

    return create_response(user_profiles, user.user_id)


@router.get('/subject', response_model=BaseResponse[List[SubjectSchema]])
async def get_subjects(
        search: str | None = None,
        user: User = Depends(get_current_admin_user),
        semester: Semester = Depends(get_current_semester),
        session: AsyncSession = Depends(conn),
):
    subject_data = crud_subject.search_by_semester(
        semester.semester_id, session, search
    )

    subjects = [SubjectSchema.model_validate(subject) for subject in subject_data]
    return create_response(subjects, user.user_id)

@router.get('/lectures', response_model=BaseResponse[List[LectureSchema]])
async def get_subjects(
        search: str | None = None,
        user: User = Depends(get_current_admin_user),
        semester: Semester = Depends(get_current_semester),
        session: AsyncSession = Depends(conn),
):
    pass