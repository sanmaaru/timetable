from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from theme.crud import get_selected_theme, get_theme
from theme.schemas import ThemeSchema, ThemeChangeInput
from core.dependencies import get_current_user
from core.response import BaseResponse, create_response, SuccessResponse, MetaSchema
from database import User, conn

router = APIRouter(prefix='/theme', tags=['theme'])

@router.get('/')
def theme(
        user: User = Depends(get_current_user),
):
    pass


@router.get('/selected', response_model=BaseResponse[ThemeSchema])
def selected_theme(
        user: User = Depends(get_current_user),
):
    selected_theme = get_selected_theme(user)
    return create_response(user, selected_theme)

@router.put('/selected')
def change_selected_theme(
        input: ThemeChangeInput,
        user: User = Depends(get_current_user),
        session: Session = Depends(conn)
):
    theme = get_theme(input.theme_id, user, session)

    user.theme_id = theme.theme_id
    session.commit()

    return SuccessResponse(
        meta = MetaSchema(
            user_id=user.user_id,
            status=status.HTTP_202_ACCEPTED,
            responded_at=datetime.now(),
        )
    )

