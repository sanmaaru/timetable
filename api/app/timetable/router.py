from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.model import User
from app.core.database import conn
from app.core.dependencies import get_current_user
from app.core.response import create_response, BaseResponse
from app.timetable.crud import query_timetable
from app.timetable.schemas import TimetableSchema

router = APIRouter()

@router.get('/timetable', response_model=BaseResponse[TimetableSchema])
async def timetable(
        user: User = Depends(get_current_user),
        session: AsyncSession = Depends(conn)
):
    timetable = await query_timetable(user, session)

    return create_response(timetable, user.user_id)