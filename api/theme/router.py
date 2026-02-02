from datetime import datetime
from typing import Optional, List, Union

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.params import Query
from sqlalchemy.orm import Session

from theme.crud import query_selected_theme, query_theme, query_all_themes
from theme.schemas import ThemeSchema, ThemeChangeInput
from core.dependencies import get_current_user
from core.response import BaseResponse, create_response, SuccessResponse, MetaSchema
from database import conn
from auth.model import User

router = APIRouter(prefix='/theme', tags=['theme'])

@router.get('/', response_model=BaseResponse[Union[List[ThemeSchema], ThemeSchema]])
def get_theme(
        user: User = Depends(get_current_user),
        theme_id: Optional[str] = Query(None, description='theme id want to query'),
        session: Session = Depends(conn)
):
    if theme_id is None:
        themes = query_all_themes(user)
        return create_response(user, themes)

    theme = query_theme(theme_id, user, session)
    return create_response(user, theme)



@router.get('/selected', response_model=BaseResponse[ThemeSchema])
def get_selected_theme(
        user: User = Depends(get_current_user),
):
    selected_theme = query_selected_theme(user)
    return create_response(user, selected_theme)

@router.put('/selected')
def change_selected_theme(
        input: ThemeChangeInput,
        user: User = Depends(get_current_user),
        session: Session = Depends(conn)
):
    theme = query_theme(input.theme_id, user, session)

    user.theme_id = theme.theme_id
    session.commit()

    return SuccessResponse(
        meta = MetaSchema(
            user_id=user.user_id,
            status=status.HTTP_202_ACCEPTED,
            responded_at=datetime.now(),
        )
    )



