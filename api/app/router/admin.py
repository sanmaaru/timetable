from typing import List, Annotated

import structlog
from fastapi import APIRouter, Depends
from fastapi.params import Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import conn, Session
from app.core.dependencies import get_current_admin_user, get_current_semester, CurrentAdminUser, CurrentSemester
from app.core.response import BaseResponse, create_response
from app.core.types import get_role
from app.crud.auth import crud_user_info, crud_user
from app.crud.timetable import crud_subject
from app.model.auth import User
from app.model.timetable import Semester
from app.schema.auth import UserSchema
from app.schema.timetable import SubjectSchema, LectureSchema

router = APIRouter(prefix='/admin', tags=['Admin'])
logger = structlog.get_logger()

@router.get('/userInfo', response_model=BaseResponse[List[UserSchema]])
async def get_user_infos(
        user: CurrentAdminUser,
        semester: CurrentSemester,
        session: Session,
        role: Annotated[str | None, Query()] = None,
        search: Annotated[str | None, Query()] = None,
):
    user_infos = await crud_user_info.search_by_semester(
        semester.semester_id,
        session,
        role=get_role(role),
        search=search
    )

    if not user_infos:
        return create_response([], user.user_id)

    identity_ids = [u.identity_id for u in user_infos if u.identity_id]

    id_user_map = {}
    if identity_ids:
        users = await crud_user.list(
            session,
            condition=[User.identity_id.in_(identity_ids)]
        )
        id_user_map = {u.identity_id: u for u in users}

    user_profiles = []
    for info in user_infos:
        u = id_user_map.get(info.identity_id)
        if u is None:
            mock_user = UserSchema(
                user_id=None,
                email=None,
                username=None,
                user_info=info,
                identity_id=info.identity_id,
            )
            user_profiles.append(mock_user)
            continue

        user_profiles.append(UserSchema(
            user_id=u.user_id,
            email=u.email,
            username=u.username,
            identity_id=u.identity_id,
            user_info=info
        ))

    return create_response(user_profiles, user.user_id)



@router.get('/subject', response_model=BaseResponse[List[SubjectSchema]])
async def get_subjects(
        user: Annotated[User, Depends(get_current_admin_user)],
        semester: Annotated[Semester, Depends(get_current_semester)],
        session: Annotated[AsyncSession, Depends(conn)],
        search: Annotated[str | None, Query()] = None,
):
    subject_data = await crud_subject.search_by_semester(
        semester.semester_id, session, search
    )

    subjects = [SubjectSchema.model_validate(subject) for subject in subject_data]
    return create_response(subjects, user.user_id)

@router.get('/lectures', response_model=BaseResponse[List[LectureSchema]])
async def get_subjects(
        user: Annotated[User, Depends(get_current_admin_user)],
        semester: Annotated[Semester, Depends(get_current_semester)],
        session: Annotated[AsyncSession, Depends(conn)],
        search: Annotated[str | None, Query()] = None,
):
    pass