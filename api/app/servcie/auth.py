from datetime import datetime, timedelta, timezone

import ulid
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from jose import jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import configs
from app.core.database import ULID
from app.crud.auth import crud_user, crud_identify_token, crud_refresh_token
from app.crud.theme import service_create_default_theme
from app.exceptions.auth import AuthorizationError
from app.exceptions.base import ConflictError
from app.model.auth import User, IdentifyToken, RefreshToken
from app.sync.model import SyncStatus

hasher = PasswordHasher()
class AuthTokenService:

    @staticmethod
    def issue_access(user_id: ULID, expired_after: timedelta | None = None):
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


    @staticmethod
    async def issue_refresh(owner_id: ULID, session: AsyncSession, expired_after: timedelta | None = None):
        issued_at = datetime.now(timezone.utc)

        if expired_after is None:
            expired_after = timedelta(days=configs.REFRESH_TOKEN_EXPIRE_DAY)
        expired_at = issued_at + expired_after


        refresh_token = RefreshToken(
            owner_id=owner_id,
            issued_at=issued_at,
            expired_at=expired_at,
        )

        crud_refresh_token.insert(refresh_token, session)
        return refresh_token


    @staticmethod
    async def reissue_refresh(
            owner_id: ULID,
            refresh: ULID,
            session: AsyncSession,
            expired_after: timedelta | None = None
    ):
        now = datetime.now(timezone.utc)
        if (refresh.expired_at < now) or refresh.owner_id != owner_id:
            raise AuthorizationError(f'Refresh token of {owner_id} is already expired')

        crud_refresh_token.delete(session, condition=[RefreshToken.owner_id == owner_id])

        new_refresh = await AuthTokenService.issue_refresh(owner_id, session, expired_after)
        return new_refresh


class AuthService:

    @staticmethod
    async def signup(
            email: str,
            username: str,
            password: str,
            identify_token: str,
            session: AsyncSession
    ):
        token = crud_identify_token.query(session, condition=[IdentifyToken.token_id == identify_token])
        if token is None:
            raise AuthorizationError(message='Unknown identify token', payload={'invalid': 'identify_token'})

        if token.expired:
            raise AuthorizationError(message='Token already used', payload={'invalid': 'identify_token'})

        # Check duplicated user exists in the database
        email, username, password = email, username, password

        queried_user = await crud_user.query(session, condition=[User.username == username])
        if queried_user:
            raise ConflictError(message='Username already exists', payload={'username': username, 'invalid': 'username'})

        # user 등록 로직
        hashed = hasher.hash(password)
        identity_id = token.identity_id

        user = User(username=username, password=hashed, email=str(email), identity_id=identity_id)
        crud_user.insert(user, session)

        theme = await service_create_default_theme(user, session)
        user.selected_theme = theme

        session.add(SyncStatus(user_id=user.user_id))

        # Make identify token expired
        token.expired = True
        await session.flush()

        return user


    @staticmethod
    async def login(
            username: str,
            password: str,
            session: AsyncSession
    ):
        user = crud_user.query(session, condition=[User.username == username])

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
        access = AuthTokenService.issue_access(user_id)
        refresh = await AuthTokenService.issue_refresh(user_id, session)

        refresh = refresh.token_id

        return access, refresh


    @staticmethod
    async def refresh(
            refresh: str,
            session: AsyncSession
    ):
        refresh_token = crud_refresh_token.query(session, condition=[RefreshToken.token_id == refresh])
        if refresh_token is None:
            raise AuthorizationError(message='Invalid refresh token', payload={'invalid': 'refresh_token'})

        user_id = refresh_token.owner_id
        new_refresh = await AuthTokenService.reissue_refresh(user_id, ulid.from_str(refresh), session)

        new_access = AuthTokenService.issue_access(user_id)

        await session.flush()
        return new_access, new_refresh.token_id

