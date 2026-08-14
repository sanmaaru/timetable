from typing import List, Optional

from fastapi import APIRouter, Depends, status, Path
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.auth import crud_identify_token
from app.model.auth import IdentifyToken
from app.schema.auth import TokenPair, LoginInput, SignUpInput, UserSchema, RefreshTokenInput, IdentifyTokenSchema
from app.core.database import conn
from app.core.dependencies import get_current_admin_user
from app.core.response import create_response, BaseResponse
from app.schema.upload import IdentityIdStr
from app.servcie.auth import AuthService

router = APIRouter(prefix='/auth', tags=['auth'])

# ===== Login =====
@router.post('/login', response_model=BaseResponse[TokenPair])
async def login(input: LoginInput, session: AsyncSession = Depends(conn)):
    access, refresh = await AuthService.login(input.username, input.password, session)
    await session.commit()

    return create_response(TokenPair(access_token=access, refresh_token=refresh))


# ===== Refresh JWT =====
@router.post('/refresh', response_model=BaseResponse[TokenPair])
async def refresh(input: RefreshTokenInput, session: AsyncSession = Depends(conn)):
    token = input.refresh_token

    new_access, new_token = await AuthService.refresh(token, session)
    await session.commit()

    return create_response(TokenPair(access_token=new_access, refresh_token=new_token))


# ===== Sign Up =====
@router.post('/signup', response_model=BaseResponse[UserSchema], status_code=status.HTTP_201_CREATED)
async def signup(input: SignUpInput, session: AsyncSession = Depends(conn)):
    user = await AuthService.signup(input.email, input.username, input.password, input.identify_token, session)
    await session.commit()

    return create_response(user, user.user_id, status_code=status.HTTP_201_CREATED)


@router.get('/identifier', response_model=BaseResponse[List[IdentifyTokenSchema]])
async def all_identifiers(
        user=Depends(get_current_admin_user),
        session: AsyncSession = Depends(conn)
):
    tokens = await crud_identify_token.list(session)
    return create_response(tokens, user.user_id)


@router.get('/identifier/{identity_id}', response_model=BaseResponse[Optional[IdentifyTokenSchema]])
async def identifier(
        user = Depends(get_current_admin_user),
        identity_id: IdentityIdStr = Path(description='identity id of user who want to query'),
        session: AsyncSession = Depends(conn)
):
    token = await crud_identify_token.query(session, condition=[IdentifyToken.identity_id == identity_id])
    return create_response(token, user.user_id)