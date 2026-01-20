from typing import Annotated

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from fastapi import APIRouter, Depends, HTTPException, status
from jose import JWTError
from pydantic import BaseModel, EmailStr, Field

from .auth import issue, LOGIN_ISSUER, reissue, RefreshTokenError, IdentifyToken
from ..database import conn, User
from ..theme.crud import create_default_theme
from ..util import create_id

router = APIRouter(prefix='/auth', tags=['auth'])
hasher = PasswordHasher()

# ===== Login =====
class LoginInput(BaseModel):
    username: str
    password: str

class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = 'bearer'

@router.post('/login', response_model=TokenPair)
def login(input: LoginInput, session = Depends(conn)):
    username, password = input.username, input.password
    user = session.query(User).filter(User.username == username).one_or_none()

    # verify id
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                'invalid': 'username',
                'message': 'unknown username'
            }
        )

    # verify password     
    hashed = user.password
    try: 
        hasher.verify(hashed, password) 
    except VerifyMismatchError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail={
                'invalid': 'password',
                'message': 'wrong password'
            }
        )

    # issue JWT & refresh token
    id = user.user_id
    access, refresh = issue(id, session, LOGIN_ISSUER) 

    access = access.encode()
    refresh = refresh.token_id
    
    session.commit()
    return TokenPair(access_token=access, refresh_token=refresh)


# ===== Refresh JWT =====
class RefreshTokenInput(BaseModel):
    
    refresh_token: str
    access_token: str

@router.post('/refresh', response_model=TokenPair)
def refresh(input: RefreshTokenInput, session = Depends(conn)):
    token = input.refresh_token
    access = input.access_token

    try:
        access, refresh = reissue(session, token, access, reload_refresh=True)

        session.commit()
        return TokenPair(
            access_token=access,
            refresh_token=refresh
        )
    except (JWTError, RefreshTokenError):
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail={
                'invalid': 'token',
                'message': 'invalid token'
            }
        )


# ===== Sign Up =====
class SignUpInput(BaseModel):
    email: EmailStr
    username: Annotated[str, Field(min_length=3, max_length=20)]
    password: Annotated[str, Field(min_length=8)]
    identify_token: Annotated[str, Field(min_length=8, max_length=8)]

@router.post('/signup')
def signup(input: SignUpInput, session = Depends(conn)):
    # indentifier token을 이용해서 신원확인
    token = IdentifyToken.get_token(session, input.identify_token)
    if token == None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail= {
                'invalid': 'identify_token',
                'message': 'unknown or expired identiy token'
            }
        )

    # db에서 중복되는 유저가 있는지 확인하기
    email, username, password = input.email, input.username, input.password

    if session.query(User).filter(User.username == username).all():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, 
            detail={
                'invalid': 'username',
                'message': 'user already exists' 
            }
        )


    # user 등록 로직
    hashed = hasher.hash(password)
    user_id = create_id(email, password, username)
    user_info_id = token.user_info_id
    
    user = User(user_id=user_id, username=username, password=hashed, email=str(email), user_info_id=user_info_id)
    session.add(user)
    create_default_theme(user, session)

    # 회원가입 완료시 identifer 삭제
    token.drop(session)
    session.commit()