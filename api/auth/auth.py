from fastapi import APIRouter, Depends, HTTPException, Response, status
from pydantic import BaseModel, EmailStr, Field
from typing import Annotated
from database import conn, User, UserInfo
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from util import hash_with_base64
from jose import JWTError
from sqlalchemy.orm import Session
from .auth_token import issue, LOGIN_ISSUER, reissue, RefreshTokenError, IdentifyToken
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
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='invalid tokens')


# ===== Sign Up =====
class SignUpInput(BaseModel):
    email: EmailStr
    id: Annotated[str, Field(min_length=3, max_length=20)]
    password: Annotated[str, Field(min_length=3)]
    identifier: Annotated[str, Field(min_length=8, max_length=8)]

@router.post('/signup')
def signup(input: SignUpInput, session = Depends(conn)):
    # indentifier token을 이용해서 신원확인
    token = IdentifyToken.get_token(session, input.identifier)
    if token == None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="unknown identifier")

    # db에서 중복되는 유저가 있는지 확인하기
    email, id, password = input.email, input.id, input.password

    if session.query(User).filter(User.id == id).all():
        raise HTTPException(status_code=400, detail='user already exists')

    if session.query(User).filter(User.email == email).all(): 
        raise HTTPException(status_code=400, detail='user already exists')

    # user 등록 로직
    hasehd = hasher.hash(password)
    user_id = _create_id(email, id)
    user_info_id = token.user_info_id
    
    user = User(user_id=user_id, id=id, password=hasehd, email=email, user_info_id=user_info_id)
    session.add(user)

    # 회원가입 완료시 identifer 삭제
    token.drop(session)
    session.commit()        


def create_user_info(session: Session, name: str, role: str, 
                       generation: int | None = None, clazz: int | None = None, number: int | None = None, credit: int | None = None):
    user_info_id = _create_id(name, role)
    
    user_info = session.query(UserInfo).filter(UserInfo.name == name,
                                               UserInfo.role == role,
                                               UserInfo.generation == generation,
                                               UserInfo.clazz == clazz,
                                               UserInfo.number == number,
                                               UserInfo.credit == credit).one_or_none()
    if user_info != None:
        raise ValueError('multiple user exists')
                                               

    user_info = UserInfo(user_info_id=user_info_id, name=name, role=role, generation=generation, clazz=clazz, number=number, credit=credit)
    session.add(user_info)
    id_token = IdentifyToken.issue(session, user_info_id)


def _create_id(s1, s2):
    hashed_email = hash_with_base64(s1, 16)
    hashed_id = hash_with_base64(s2, 12)
    hashed_random = hash_with_base64(random.randint(0, 999), 4)

    id = f"{hashed_email}-{hashed_id}.{hashed_random}=="
    return id