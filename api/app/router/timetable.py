from typing import List, Annotated

import structlog
from fastapi import APIRouter, Depends, Path
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import conn
from app.core.dependencies import get_current_user, get_current_semester
from app.core.response import create_response, BaseResponse
from app.core.types import ULIDModel
from app.crud.auth import crud_user_info
from app.crud.timetable import crud_lecture, crud_enrollment
from app.exceptions.base import NotFoundError
from app.model.auth import User
from app.model.timetable import Lecture, Semester
from app.schema.auth import UserInfoSchema
from app.schema.timetable import TimetableSchema, LectureSchema
from app.servcie.timetable import TimetableService
from app.sync.dependencies import get_status_dependency
from app.sync.schemas import VersionResponse

logger = structlog.get_logger()

router = APIRouter(prefix='/timetable', tags=['Timetable'])
theme_status_dep = get_status_dependency('timetable')

@router.get('/status', response_model=BaseResponse[VersionResponse])
async def get_theme_status(
        user: User = Depends(get_current_user),
        timetable_status: VersionResponse = Depends(theme_status_dep),
):
    return create_response(timetable_status, user.user_id)


@router.get('/', response_model=BaseResponse[TimetableSchema])
async def get_timetable(
        user: Annotated[User, Depends(get_current_user)],
        semester: Annotated[Semester, Depends(get_current_semester)],
        session: Annotated[AsyncSession, Depends(conn)]
):
    timetable, name = await TimetableService.query_timetable(
        user.identity_id, semester, session
    )

    logger.info(await crud_enrollment.list(session))

    schema = TimetableSchema(
        username=user.username,
        name=name,
        timetable=timetable,
    )

    return create_response(schema, user.user_id)


@router.get('/lecture/{lecture_id}', response_model=BaseResponse[LectureSchema])
async def get_class(
        user: Annotated[User, Depends(get_current_user)],
        semester: Annotated[Semester, Depends(get_current_semester)],
        lecture_id: Annotated[ULIDModel, Path(description='class id you want to query')],
        session: Annotated[AsyncSession, Depends(conn)]
):
    lecture = await crud_lecture.query_with_detail(
        semester.semester_id, session,
        condition=[Lecture.lecture_id == lecture_id],
    )
    if not lecture:
        raise NotFoundError(f'Cannot find lecture of {lecture_id} in {semester.code}')

    return create_response(lecture, user.user_id)


@router.get('/classmates/{lecture_id}', response_model=BaseResponse[List[UserInfoSchema]])
async def get_classmate(
        user: Annotated[User, Depends(get_current_user)],
        semester: Annotated[Semester, Depends(get_current_semester)],
        lecture_id: Annotated[ULIDModel, Path(description='class id you want to query')],
        session: Annotated[AsyncSession, Depends(conn)]
):
    classmates = await TimetableService.query_classmates(lecture_id, semester, session)

    return create_response(classmates, user.user_id)