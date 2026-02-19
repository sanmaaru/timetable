from typing import List

from fastapi import APIRouter, Depends, status
from fastapi.params import Path, Body
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.model import User
from app.core.dependencies import get_current_user
from app.core.response import BaseResponse, create_response, SuccessResponse, MetaSchema
from app.core.types import ULIDModel
from app.core.database import conn
from app.sync.dependencies import get_status_dependency
from app.sync.schemas import VersionResponse
from app.theme.crud import query_selected_theme, query_theme, query_all_themes, service_delete_theme, \
    service_change_selected_theme, service_create_default_theme, service_change_theme
from app.theme.schemas import ThemeSchema, SelectedThemeChangeInput, ThemeCreateInput, ThemeChangeInput

router = APIRouter(prefix='/theme', tags=['theme'])
theme_status_dep = get_status_dependency('theme')

@router.get('/status', response_model=VersionResponse)
async def get_theme_status(
        theme_status: VersionResponse = Depends(theme_status_dep),
):
    return theme_status

@router.get('/', response_model=BaseResponse[List[ThemeSchema]])
async def get_themes(
        user: User = Depends(get_current_user),
        session: AsyncSession = Depends(conn)
):
    themes = await query_all_themes(user, session)
    return create_response(themes, user.user_id)

@router.post('/', response_model=BaseResponse[ThemeSchema], status_code=status.HTTP_201_CREATED)
async def post_theme(
        input: ThemeCreateInput,
        user: User = Depends(get_current_user),
        session: AsyncSession = Depends(conn)
):
    theme = await service_create_default_theme(user, session, input.title)
    await session.commit()
    return create_response(theme, user.user_id)

@router.get('/selected', response_model=BaseResponse[ThemeSchema])
async def get_selected_theme(
        user: User = Depends(get_current_user),
        session: AsyncSession = Depends(conn)
):
    selected_theme = await query_selected_theme(user, session)
    return create_response(selected_theme, user.user_id)

@router.put('/selected')
async def change_selected_theme(
        input: SelectedThemeChangeInput,
        user: User = Depends(get_current_user),
        session: AsyncSession = Depends(conn)
):
    theme_id = input.theme_id
    await service_change_selected_theme(user, theme_id, session)
    await session.commit()

    return SuccessResponse(
            meta = MetaSchema(
                user_id=str(user.user_id),
                status=status.HTTP_202_ACCEPTED,
            )
    )

@router.get('/{theme_id}', response_model=BaseResponse[ThemeSchema])
async def get_theme(
        user: User = Depends(get_current_user),
        theme_id: ULIDModel = Path(description='theme id want to query'),
        session: AsyncSession = Depends(conn)
):
    theme = await query_theme(theme_id, user, session)
    return create_response(theme, user.user_id)

@router.delete('/{theme_id}')
async def delete_theme(
        theme_id: ULIDModel = Path(description='theme id want to delete'),
        user: User = Depends(get_current_user),
        session: AsyncSession = Depends(conn)
):
    await service_delete_theme(user, theme_id, session)
    await session.commit()
    return SuccessResponse(
        meta = MetaSchema(
            user_id=str(user.user_id),
            status=status.HTTP_202_ACCEPTED,
        )
    )

@router.put('/{theme_id}')
async def put_theme(
        theme_id: ULIDModel = Path(description='theme id want to change'),
        input: ThemeChangeInput = Body(description='theme data to change'),
        user: User = Depends(get_current_user),
        session: AsyncSession = Depends(conn)
):
    await service_change_theme(user, theme_id, session, input.title, input.color_schemes)
    await session.commit()
    return SuccessResponse(
        meta=MetaSchema(
            user_id=str(user.user_id),
            status=status.HTTP_202_ACCEPTED,
        )
    )