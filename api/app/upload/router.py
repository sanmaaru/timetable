from pathlib import Path
from typing import List

from fastapi import APIRouter
from fastapi.params import Depends
from starlette.responses import JSONResponse

from app.core.database import conn
from app.upload.upload import *

router = APIRouter(prefix="/upload", tags=["Upload"])

@router.get("/", response_model=List[UserInfoData])
async def healthy():
    return JSONResponse('healthy: ' + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

# TODO: for the debugging
@router.post('/init')
async def initialize(
        session: AsyncSession = Depends(conn)
):
    if not configs.DEBUG:
        raise AuthorizationError('Not authorized')

    resources = Path(__file__).parent.parent.parent / 'resources'

    enrollments_path = resources / 'enrollment.xlsx'
    lecture_path = resources / 'lecture.xlsx'
    period_path = resources / 'period.xlsx'

    enrollments, periods = parse_enrollments(str(enrollments_path))
    lectures = parse_lectures(str(lecture_path))
    multi_tch_periods = parse_periods(str(period_path))
    periods = unify_periods(periods, multi_tch_periods, lectures)

    await upload_teachers(lectures, session)
    await upload_students(enrollments, session)
    await upload_lectures(lectures, session)
    await upload_periods(periods, session)
    await upload_enrollments(enrollments, session)

    stmt = select(UserInfo).where(UserInfo.name == 'admin')
    result = await session.execute(stmt)
    if result.scalars().one_or_none() is None:
        await create_user_info(session, UserInfoData('admin'), role=Role.ADMINISTRATOR)

    await session.commit()

    # return create_response(await query_token_for('admin', session))