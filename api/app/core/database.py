import binascii
from typing import Any

import ulid
from sqlalchemy import (
    TypeDecorator, BINARY, LargeBinary
)
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase

from app.core.config import configs

engine = create_async_engine(
    configs.DATABASE_URL,
    echo=configs.DEBUG, # 디버그 모드일 때 SQL 로그 출력
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