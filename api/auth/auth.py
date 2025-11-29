from fastapi import APIRouter, Depends, HTTPException, Response, status
from pydantic import BaseModel, EmailStr, Field
from typing import Annotated
from database import conn, User
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from util import hash_with_base64
from jose import JWTError
from auth_token import issue, LOGIN_ISSUER, reissue, RefreshTokenError
import random, dotenv, os

dotenv.load_dotenv()


router = APIRouter(prefix='/auth', tags=['auth'])
hasher = PasswordHasher()

# ===== Login =====
class LoginInput(BaseModel):
    id: str
    password: str

class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = 'bearer'

@router.post('/login', response_model=TokenPair)
def login(input: LoginInput, session = Depends(conn)):
    id, password = input.id, input.password
    user = session.query(User).filter(User.id == id).one_or_none()

    # verify id
    if not user:
        raise HTTPException(status_code=400, detail='unknown id')

    # verify password     
    hashed = user.password
    try: 
        hasher.verify(hashed, password) 
    except VerifyMismatchError:
        raise HTTPException(status_code=400, detail='invalid password')

    # issue JWT & refresh token
    id = user.user_id
    access, refresh = issue(id, session, LOGIN_ISSUER) 

    access = access.encode()
    refresh = refresh.token_id

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
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='invalid tokens')


# ===== Sign Up =====
class SignUpInput(BaseModel):
    email: EmailStr
    name: Annotated[str, Field(min_length=1, max_length=10)]
    id: Annotated[str, Field(min_length=3, max_length=20)]
    password: Annotated[str, Field(min_length=3)]
    role: str = 'stu'
@router.post('/signup')
def signup(input: SignUpInput, session = Depends(conn)):
    # db에서 중복되는 유저가 있는지 확인하기
    email, id, password, name, role = input.email, input.id, input.password, input.name, input.role 

    if session.query(User).filter(User.id == id).all():
        raise HTTPException(status_code=400, detail='user already exists')

    if session.query(User).filter(User.email == email).all(): 
        raise HTTPException(status_code=400, detail='user already exists')

    # user 등록 로직
    hasehd = hasher.hash(password)
    user_id = _create_user_id(email, id)
    
    user = User(user_id=user_id, id=id, password=hasehd, email=email, name=name, role=role)
    session.add(user)
    session.commit()        


def _create_user_id(email, id):
    hashed_email = hash_with_base64(email, 16)
    hashed_id = hash_with_base64(id, 12)
    hashed_random = hash_with_base64(random.randint(0, 999), 4)

    id = f"{hashed_email}-{hashed_id}.{hashed_random}=="
    return id