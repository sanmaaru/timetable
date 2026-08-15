import datetime
import json
from typing import List

from fastapi import APIRouter, UploadFile
from fastapi.params import Depends, Body
from pydantic import ValidationError
from starlette.responses import JSONResponse

from app.core.database import conn
from app.core.dependencies import get_current_admin_user, get_current_semester
from app.core.response import BaseResponse, create_response, SuccessResponse, MetaSchema
from app.crud.timetable import crud_lecture, crud_period, crud_enrollment
from app.crud.upload import *
from app.exceptions.upload import InvalidFormatError
from app.schema.auth import UserInfoData
from app.schema.upload import UploadConfirmInput, SubjectFileSchema, UploadResponse, LectureInfoSchema, \
    LectureListSchema, PeriodListSchema, EnrollmentListSchema, StudentInfoListSchema, StudentInfoSchema, \
    TeacherInfoListSchema, TeacherInfoSchema

router = APIRouter(prefix="/upload", tags=["Upload"])


@router.get("/", response_model=List[UserInfoData])
async def healthy():
    return JSONResponse('healthy: ' + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))


@router.post("/subject", response_model=BaseResponse[UploadResponse])
async def upload_subject(
        file: UploadFile,
        semester: Semester = Depends(get_current_semester),
        user: User = Depends(get_current_admin_user),
        session: AsyncSession = Depends(conn)
):
    try:
        contents = await file.read()
        json_data = json.loads(contents)

        data: list[str] = SubjectFileSchema.model_validate(json_data).root
    except (json.JSONDecodeError, ValidationError):
        raise InvalidFormatError(message="Invalid file format")

    draft = await create_upload_draft(
        action_name='UPLOAD_SUBJECT',
        payload={
            'subjects': data,
            'semester_id': str(semester.semester_id)
        },
        session=session
    )
    is_exist = await crud_subject.count_by_semester(semester.semester_id, session)!= 0
    await session.commit()

    return create_response(
        UploadResponse(draft_id=str(draft.draft_id), is_exist=is_exist),
        user.user_id,
    )


@router.post("/lecture", response_model=BaseResponse[UploadResponse])
async def upload_lecture(
        file: UploadFile,
        semester: Semester = Depends(get_current_semester),
        user: User = Depends(get_current_admin_user),
        session: AsyncSession = Depends(conn)
):
    try:
        contents = await file.read()
        json_data = json.loads(contents)
        data: list[LectureInfoSchema] = LectureListSchema.model_validate(json_data).root
    except (json.JSONDecodeError, ValidationError):
        raise InvalidFormatError(message="Invalid file format")

    draft = await create_upload_draft(
        action_name='UPLOAD_LECTURE',
        payload={
            'lectures': data,
            'semester_id': str(semester.semester_id)
        },
        session=session
    )
    is_exist = await crud_lecture.count_by_semester(semester.semester_id, session) != 0
    await session.commit()

    return create_response(
        UploadResponse(draft_id=str(draft.draft_id), is_exist=is_exist),
        user.user_id,
    )


@router.post("/period", response_model=BaseResponse[UploadResponse])
async def upload_period(
        file: UploadFile,
        semester: Semester = Depends(get_current_semester),
        user: User = Depends(get_current_admin_user),
        session: AsyncSession = Depends(conn)
):
    try:
        contents = await file.read()
        json_data = json.loads(contents)
        data: list[PeriodInfoSchema] = PeriodListSchema.model_validate(json_data).root
    except (json.JSONDecodeError, ValidationError):
        raise InvalidFormatError(message="Invalid file format")

    draft = await create_upload_draft(
        action_name='UPLOAD_PERIOD',
        payload={
            'periods': data,
            'semester_id': str(semester.semester_id)
        },
        session=session
    )
    is_exist = await crud_period.count_by_semester(semester.semester_id, session) != 0
    await session.commit()

    return create_response(
        UploadResponse(draft_id=str(draft.draft_id), is_exist=is_exist),
        user.user_id,
    )


@router.post("/enrollment", response_model=BaseResponse[UploadResponse])
async def upload_enrollment(
        file: UploadFile,
        semester: Semester = Depends(get_current_semester),
        user: User = Depends(get_current_admin_user),
        session: AsyncSession = Depends(conn)
):
    try:
        contents = await file.read()
        json_data = json.loads(contents)
        data: list[EnrollmentInfoSchema] = EnrollmentListSchema.model_validate(json_data).root
    except (json.JSONDecodeError, ValidationError) as e:
        raise InvalidFormatError(message=f"Invalid file format")

    draft = await create_upload_draft(
        action_name='UPLOAD_ENROLLMENT',
        payload={
            'enrollments': data,
            'semester_id': str(semester.semester_id)
        },
        session=session
    )
    is_exist = crud_enrollment.count_by_semester(semester.semester_id, session) != 0
    await session.commit()

    return create_response(
        UploadResponse(draft_id=str(draft.draft_id), is_exist=is_exist),
        user.user_id,
    )


@router.post("/student")
async def upload_student(
        file: UploadFile,
        semester: Semester = Depends(get_current_semester),
        user: User = Depends(get_current_admin_user),
        session: AsyncSession = Depends(conn)
):
    try:
        contents = await file.read()
        json_data = json.loads(contents)
        data: list[StudentInfoSchema] = StudentInfoListSchema.model_validate(json_data).root
    except (json.JSONDecodeError, ValidationError):
        raise InvalidFormatError(message="Invalid file format")

    draft = await create_upload_draft(
        action_name='UPLOAD_STUDENT',
        payload={
            'students': data,
            'semester_id': str(semester.semester_id)
        },
        session=session
    )

    is_exist = crud_user_info.count_by_semester(
        semester.semester_id, session, condition=[UserInfo.role == Role.TEACHER]
    ) != 0
    await session.commit()

    return create_response(
        UploadResponse(draft_id=str(draft.draft_id), is_exist=is_exist),
        user.user_id,
    )


@router.post('/teacher')
async def upload_teacher(
        file: UploadFile,
        semester: Semester = Depends(get_current_semester),
        user: User = Depends(get_current_admin_user),
        session: AsyncSession = Depends(conn)
):
    try:
        contents = await file.read()
        json_data = json.loads(contents)
        data: list[TeacherInfoSchema] = TeacherInfoListSchema.model_validate(json_data).root
    except (json.JSONDecodeError, ValidationError):
        raise InvalidFormatError(message="Invalid file format")

    draft = await create_upload_draft(
        action_name='UPLOAD_TEACHER',
        payload={
            'teachers': data,
            'semester_id': str(semester.semester_id)
        },
        session=session
    )
    is_exist = crud_user_info.count_by_semester(
        semester.semester_id, session, condition=[UserInfo.role == Role.TEACHER]
    ) != 0
    await session.commit()

    return create_response(
        UploadResponse(draft_id=str(draft.draft_id), is_exist=is_exist),
        user.user_id,
    )


@router.post("/confirm")
async def confirm(
        confirm: UploadConfirmInput = Body(),
        user: User = Depends(get_current_admin_user),
        session: AsyncSession = Depends(conn)
):
    await apply_draft(confirm.draft_id, confirm.mode, confirm.confirm, session)
    await session.commit()

    return SuccessResponse(
        meta=MetaSchema(
            user_id=str(user.user_id),
        )
    )