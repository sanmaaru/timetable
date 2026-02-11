from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, status
from fastapi.params import Path
from sqlalchemy.orm import Session

from auth.model import User
from core.dependencies import get_current_user
from core.response import BaseResponse, create_response, SuccessResponse, MetaSchema
from core.types import ULIDModel
from database import conn
from theme.crud import query_selected_theme, query_theme, query_all_themes, service_delete_theme, \
    service_change_selected_theme, service_create_default_theme, get_theme_schema
from theme.schemas import ThemeSchema, ThemeChangeInput, ThemeCreateInput

router = APIRouter(prefix='/theme', tags=['theme'])

@router.get('/', response_model=BaseResponse[List[ThemeSchema]])
def get_theme(
        user: User = Depends(get_current_user),
):
    themes = query_all_themes(user)
    return create_response(user, themes)

@router.post('/', response_model=BaseResponse[ThemeSchema])
def post_theme(
        input: ThemeCreateInput,
        user: User = Depends(get_current_user),
        session: Session = Depends(conn)
):
    theme = service_create_default_theme(user, user.user_info, session, input.title)
    session.commit()
    return create_response(user, get_theme_schema(theme, user))

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
    theme_id = input.theme_id
    service_change_selected_theme(user, theme_id, session)
    session.commit()

    return SuccessResponse(
            meta = MetaSchema(
                user_id=user.user_id,
                status=status.HTTP_202_ACCEPTED,
                responded_at=datetime.now(),
            )
    )

@router.get('/{theme_id}', response_model=BaseResponse[ThemeSchema])
def get_theme(
        user: User = Depends(get_current_user),
        theme_id: ULIDModel = Path(description='theme id want to query'),
        session: Session = Depends(conn)
):
    theme = query_theme(theme_id, user, session)
    return create_response(user, theme)

@router.delete('/{theme_id}')
def delete_theme(
        theme_id: ULIDModel = Path(description='theme id want to delete'),
        user: User = Depends(get_current_user),
        session: Session = Depends(conn)
):
    service_delete_theme(user, theme_id, session)
    session.commit()
    return SuccessResponse(
        meta = MetaSchema(
            user_id=user.user_id,
            status=status.HTTP_202_ACCEPTED,
            responded_at=datetime.now(),
        )
    )


