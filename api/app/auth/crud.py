from datetime import timezone, datetime, timedelta

import ulid
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from jose import jwt, JWTError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import with_expression, joinedload
from ulid import ULID

from app.auth.exceptions import AuthorizationError, RefreshTokenError
from app.auth.model import User, UserInfo, IdentifyToken, RefreshToken
from app.core.config import configs
from app.core.exceptions import ConflictError
from app.auth.schemas import TokenPayload, UserInfoData
from app.theme.crud import service_create_default_theme

hasher = PasswordHasher()

class Role:

    STUDENT=1
    TEACHER=2
    MANAGER=4
    ADMINISTRATOR=8

async def create_user_info(session: AsyncSession, user_info_data: UserInfoData, role: int):
    stmt = select(UserInfo).filter(UserInfo.name == user_info_data.name,
                                   UserInfo.generation == user_info_data.generation,
                                   UserInfo.clazz == user_info_data.clazz,
                                   UserInfo.number == user_info_data.number,
                                   UserInfo.credit == user_info_data.credit)
    user_info = (await session.execute(stmt)).scalars().one_or_none()
    if user_info is not None:
        raise ConflictError('Multiple user exists', payload={'conflict': user_info.user_info_id})

    user_info = UserInfo(
        name=user_info_data.name,
        role=role,
        generation=user_info_data.generation,
        clazz=user_info_data.clazz,
        number=user_info_data.number,
        credit=user_info_data.credit
    )

    session.add(user_info)
    await session.flush()

    id_token = IdentifyToken(user_info_id=user_info.user_info_id)
    session.add(id_token)

### ==== About Identify Token ====
async def query_token(identify_token, session):
    stmt = select(IdentifyToken).filter(IdentifyToken.token_id == identify_token)
    token = (await session.execute(stmt)).scalars().one_or_none()

    return token

async def query_tokens(session):
    stmt = (select(IdentifyToken).options(joinedload(IdentifyToken.user_info)))

    tokens = (await session.execute(stmt)).scalars().all()

    return tokens

async def query_token_for(name, session):
    stmt = (select(IdentifyToken)
            .join(IdentifyToken.user_info)
            .where(UserInfo.name == name)
            .options(joinedload(IdentifyToken.user_info)))
    tokens = (await session.execute(stmt)).scalars().all()

    return tokens

async def grant_authority(user_id: str, role: int, session: AsyncSession):
    stmt = select(User).filter(User.user_id == user_id)
    user = (await session.execute(stmt)).scalars().one_or_none()

    if user is None:
        raise AuthorizationError(message='User not found', payload={'user_id': user_id})

    user_info = user.user_info
    user_info.role = user_info.role | role
    await session.flush()

### ==== About Access Token ====
def issue_access(user_id: ULID, expired_after: timedelta = None):
    issued_at = datetime.now(timezone.utc)

    if expired_after is None:
        expired_after = timedelta(minutes=configs.JWT_EXPIRE_MINUTES)
    expired_at = issued_at + expired_after

    payload = {
        'sub': str(user_id),
        'iat': issued_at,
        'exp': expired_at
    }

    encoded = jwt.encode(payload, configs.JWT_SECRET, configs.JWT_ALGORITHM)
    return encoded

def decode_access(access: str):
    try:
        payload = jwt.decode(access, configs.JWT_SECRET, algorithms=[configs.JWT_ALGORITHM])
        data = TokenPayload(**payload)

        if data.sub is None:
            raise AuthorizationError('Token missing subject (user_id)')

        return data
    except JWTError:
        raise AuthorizationError('Could not validate credentials')

### ==== About Refresh ====
async def issue_refresh(session: AsyncSession, owner_id: ULID, expired_after: timedelta = None):
    issued_at = datetime.now(timezone.utc)

    if expired_after is None:
        expired_after = timedelta(days=configs.REFRESH_TOKEN_EXPIRE_DAY)
    expired_at = issued_at + expired_after


    refresh_token = RefreshToken(
        owner_id=owner_id,
        issued_at=issued_at,
        expired_at=expired_at,
    )

    session.add(refresh_token)
    await session.flush()
    return refresh_token

async def reissue_refresh(session: AsyncSession, user_id: ULID, refresh: ULID, expired_after: timedelta = None):
    stmt = select(RefreshToken).filter(RefreshToken.token_id == refresh)
    refresh_token = (await (session.execute(stmt))).scalars().one_or_none()

    if refresh_token:
        await session.delete(refresh_token)
        await session.flush()

    new_refresh = await issue_refresh(session, user_id, expired_after)
    return new_refresh

async def query_refresh(refresh: ULID, session: AsyncSession):
    stmt = (select(RefreshToken)
            .filter(RefreshToken.token_id == refresh)
            .options(joinedload(RefreshToken.owner)))
    refresh_token = (await session.execute(stmt)).scalars().one_or_none()

    if refresh_token is None:
        raise RefreshTokenError('Unknown refresh token')

    return refresh_token

def verify_refresh(refresh: RefreshToken, owner_id: ULID):
    now = datetime.now(timezone.utc)
    if refresh.expired_at < now:
        return False

    if refresh.owner_id != owner_id:
        return False

    return True


### ==== About Services ====
async def service_signup(
        email: str,
        username: str,
        password: str,
        identify_token: str,
        session: AsyncSession
):
    token = await query_token(identify_token, session)
    if token is None:
        raise AuthorizationError(message='Invalid identify token', payload={'invalid': 'identify_token'})

    # db에서 중복되는 유저가 있는지 확인하기
    email, username, password = email, username, password

    stmt = select(User).filter(User.username == username)
    if (await session.execute(stmt)).scalars().all():
        raise ConflictError(message='Username already exists', payload={'username': username, 'invalid': 'username'})

    # user 등록 로직
    hashed = hasher.hash(password)
    user_info_id = token.user_info_id

    user = User(username=username, password=hashed, email=str(email), user_info_id=user_info_id)
    session.add(user)
    await session.flush()

    theme = await service_create_default_theme(user, session)
    user.selected_theme = theme

    # 회원가입 완료시 identifer 삭제
    await session.delete(token)
    await session.flush()

    return user

async def service_login(username: str, password: str, session: AsyncSession):
    stmt = select(User).filter(User.username == username)
    user = (await session.execute(stmt)).scalars().one_or_none()

    # verify id
    if not user:
        raise AuthorizationError(message='Unknown username', payload={'invalid': 'username'})

    # verify password
    hashed = user.password
    try:
        hasher.verify(hashed, password)
    except VerifyMismatchError:
        raise AuthorizationError(message='Invalid password', payload={'invalid': 'password'})

    # issue JWT & refresh token
    user_id = user.user_id
    access = issue_access(user_id)
    refresh = await issue_refresh(session, user_id)

    refresh = refresh.token_id

    return access, refresh

async def service_refresh(refresh: str, session: AsyncSession):
    try:
        refresh_token = await query_refresh(ulid.from_str(refresh), session)

        user_id = refresh_token.owner_id
        new_refresh = await reissue_refresh(session, user_id, ulid.from_str(refresh))

        new_access = issue_access(user_id)

        await session.commit()
        return new_access, new_refresh.token_id
    except RefreshTokenError:
        raise AuthorizationError(message='Invalid refresh token', payload={'invalid': 'refresh_token'})