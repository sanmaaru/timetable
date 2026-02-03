from datetime import datetime
from typing import Optional, List, Union

import ulid
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.params import Query, Path
from sqlalchemy.orm import Session

from core.types import ULIDInput
from theme.crud import query_selected_theme, query_theme, query_all_themes, service_delete_theme, \
    service_change_selected_theme
from theme.schemas import ThemeSchema, ThemeChangeInput
from core.dependencies import get_current_user
from core.response import BaseResponse, create_response, SuccessResponse, MetaSchema
from database import conn
from auth.model import User

router = APIRouter(prefix='/theme', tags=['theme'])

@router.get('/', response_model=BaseResponse[List[ThemeSchema]])
def get_theme(
        user: User = Depends(get_current_user),
):
    themes = query_all_themes(user)
    return create_response(user, themes)

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
    if isinstance(theme_id, str):
        theme_id = ulid.from_str(theme_id)

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
        theme_id: ULIDInput = Path(description='theme id want to query'),
        session: Session = Depends(conn)
):
    theme = query_theme(theme_id, user, session)
    return create_response(user, theme)

@router.delete('/{theme_id}')
def delete_theme(
        theme_id: ULIDInput = Path(description='theme id want to delete'),
        user: User = Depends(get_current_user),
        session: Session = Depends(conn)
):
    if isinstance(theme_id, str):
        theme_id = ulid.from_str(theme_id)

    service_delete_theme(user, theme_id, session)
    session.commit()
    return SuccessResponse(
        meta = MetaSchema(
            user_id=user.user_id,
            status=status.HTTP_202_ACCEPTED,
            responded_at=datetime.now(),
        )
    )


