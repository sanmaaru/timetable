from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr, Field
from typing import Annotated
from database import conn, User
from argon2 import PasswordHasher
import uuid

router = APIRouter(prefix='/auth', tags=['auth'])
hasher = PasswordHasher()

# ===== Login =====
class LoginInput(BaseModel):
    id: str
    password: str

@router.post('/login')
def login(input: LoginInput, session = Depends(conn)):
    id, password = input.id, input.password
    user = session.query(User).filter(User.id == id).first()

    # verify id
    if not user:
        raise HTTPException(status_code=400, detail='unknown id')

    # verify password     
    hashed = user.password
    if not hasher.verify(password, hashed): 
        raise HTTPException(status_code=400, detail='invalid password')

    # issue JWT & refresh token
    id = user.user_id

# ===== Sign Up =====
class SignUpInput(BaseModel):
    email: EmailStr
    id: Annotated[str, Field(min_length=3, max_length=20)]
    password: Annotated[str, Field(min_length=3)]

@router.post('/signup')
def signup(input: SignUpInput, session = Depends(conn)):
    # db에서 중복되는 유저가 있는지 확인하기
    email, id, password = input.email, input.id, input.password

    if session.query(User).filter(User.id == id).all():
        raise HTTPException(status_code=400, detail='user already exists')

    if session.query(User).filter(User.email == email).all(): 
        raise HTTPException(status_code=400, detail='user already exists')

    # user 등록 로직
    hasehd = hasher.hash(password)
    user_id = uuid.uuid4()
    ## uuid 곂침 처리
    while session.query(User.user_id).filter(User.user_id == user_id).first() is not None:
        user_id = uuid.uuid4()
    
    user = User(user_id=user_id, id=id, password=hasehd, email=email)
    session.add(user)
    session.commit()        

def _create_user_id(email, id, password):
    