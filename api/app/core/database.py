import binascii
import pickle
import re
from typing import Any, Optional

import ulid
from sqlalchemy import (
    TypeDecorator, BINARY, LargeBinary, String, Dialect
)
from sqlalchemy.dialects.mysql import LONGBLOB
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.sql.type_api import _T

from app.core.config import configs

engine = create_async_engine(
    configs.DATABASE_URL,
    echo=False, # 디버그 모드일 때 SQL 로그 출력
    pool_pre_ping=True,
    pool_size=20,
    max_overflow=10
)

class ULID(TypeDecorator):

    impl = BINARY(16)
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return None

        if isinstance(value, str):
            value = ulid.from_str(value)

        return value.bytes

    def process_result_value(self, value, dialect):
        if value is None:
            return None

        return ulid.from_bytes(value)


class IdentityId(TypeDecorator):

    impl = String(16)
    cache_ok = True

    PATTERN = re.compile(r'^[0-9][0-9]{2}-[0-9a-fA-F]{12}$')

    def process_bind_param(self, value, dialect):
        if value is None:
            return None

        if not isinstance(value, str):
            raise ValueError('Identity id must be a string')

        if len(value) != 16:
            raise ValueError('Identity id must be a 16 characters long')

        if not self.PATTERN.match(value):
            raise ValueError('Invalid identity id')

        return value


    def process_result_value(self, value, dialect):
        return value


class LargePickleType(TypeDecorator):
    impl = LONGBLOB
    cache_ok = True

    def process_bind_param(self, value: Optional[_T], dialect: Dialect) :
        if value is not None:
            return pickle.dumps(value)
        return None

    def process_result_value(self, value: Optional[_T], dialect: Dialect) :
        if value is not None:
            return pickle.loads(value)
        return None


def generate_ulid():
    return ulid.new()

class Hex(TypeDecorator):

    impl = LargeBinary
    cache_ok = True

    def __init__(self, length = None, **kwargs):
        if length is not None:
            length = (length + 1) // 2
            super().__init__(length=length, **kwargs)
        else:
            super().__init__(**kwargs)

    def process_bind_param(self, value: str, dialect) -> Any:
        if value is None:
            return None

        value = value.replace("#", "").replace('0x', '').strip()
        if len(value) % 2 != 0:
            value = '0' + value

        return binascii.unhexlify(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return None

        return binascii.hexlify(value).decode('utf-8')


## Tables
class Base(DeclarativeBase):
    pass

# ===== Basic =====
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False, # 비동기에서 필수 (커밋 후 속성 접근 시 에러 방지)
    autoflush=False
)

async def conn():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


# ===== Default Data Creation ======