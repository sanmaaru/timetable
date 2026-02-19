from fastapi import APIRouter, Depends, Path
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.model import User
from app.core.database import conn
from app.core.dependencies import get_current_user
from app.core.response import create_response, BaseResponse
from app.core.types import ULIDModel
from app.sync.dependencies import get_status_dependency
from app.sync.schemas import VersionResponse
from app.timetable.crud import query_timetable, query_class
from app.timetable.schemas import TimetableSchema, ClassSchema

router = APIRouter()
theme_status_dep = get_status_dependency('timetable')

@router.get('/timetable/status', response_model=VersionResponse)
async def get_theme_status(
        timetable_status: VersionResponse = Depends(theme_status_dep),
):
    return timetable_status

@router.get('/timetable', response_model=BaseResponse[TimetableSchema])
async def get_timetable(
        user: User = Depends(get_current_user),
        session: AsyncSession = Depends(conn)
):
    timetable = await query_timetable(user, session)

    return create_response(timetable, user.user_id)

@router.get('/class/{class_id}', response_model=BaseResponse[ClassSchema])
async def get_class(
        user: User = Depends(get_current_user),
        class_id: ULIDModel = Path(description='class id you want to query'),
        session: AsyncSession = Depends(conn)
):
    classes = await query_class(class_id, session)

    return create_response(classes, user.user_id)