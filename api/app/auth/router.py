from typing import Optional, List

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Query

from app.auth.crud import service_signup, service_login, service_refresh, Role, query_tokens
from app.auth.exceptions import NoPermissionError
from app.auth.model import IdentifyToken
from app.auth.schemas import TokenPair, LoginInput, SignUpInput, UserSchema, RefreshTokenInput, IdentifyTokenSchema
from app.core.dependencies import get_current_user
from app.core.response import create_response, BaseResponse
from app.core.database import conn

router = APIRouter(prefix='/auth', tags=['auth'])

# ===== Login =====
@router.post('/login', response_model=BaseResponse[TokenPair])
async def login(input: LoginInput, session: AsyncSession = Depends(conn)):
    access, refresh = await service_login(input.username, input.password, session)
    await session.commit()

    return create_response(TokenPair(access_token=access, refresh_token=refresh))


# ===== Refresh JWT =====


@router.post('/refresh', response_model=BaseResponse[TokenPair])
async def refresh(input: RefreshTokenInput, session: AsyncSession = Depends(conn)):
    token = input.refresh_token
    access = input.access_token

    new_access, new_token = await service_refresh(token, access, session)
    await session.commit()

    return create_response(TokenPair(access_token=new_access, refresh_token=new_token))


# ===== Sign Up =====
@router.post('/signup', response_model=BaseResponse[UserSchema], status_code=status.HTTP_201_CREATED)
async def signup(input: SignUpInput, session: AsyncSession = Depends(conn)):
    user = await service_signup(input.email, input.username, input.password, input.identify_token, session)
    await session.commit()

    return create_response(user, user.user_id, status_code=status.HTTP_201_CREATED)


@router.get('/identifiers', response_model=BaseResponse[List[IdentifyTokenSchema]])
async def identifiers(
        user=Depends(get_current_user),
        session: AsyncSession = Depends(conn)
):
    if user.user_info.role < Role.MANAGER:
        raise NoPermissionError('No permission')

    tokens = await query_tokens(session)

    return create_response(tokens, user.user_id)