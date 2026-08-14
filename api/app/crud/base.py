from typing import TypeVar, Generic, Type, Any

from sqlalchemy import select, func, inspect, delete, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase
from ulid.ulid import ULID

from app.core.database import Base
from app.model.timetable import SemesterMixin
from sqlalchemy.dialects.mysql import insert as mysql_insert


def get_state_dict(item: dict[str, Any] | DeclarativeBase):
    if isinstance(item, dict):
        item_dict = item.copy()
    elif isinstance(item, DeclarativeBase) or hasattr(item, "_sa_instance_state"):
        state = inspect(item)
        item_dict = {}
        for attr in state.mapper.column_attrs:
            for attr.key in state.dict:
                item_dict[attr.key] = state.dict[attr.key]
    else:
        raise TypeError(f"Unsupported data type in insert list: {type(item)}")

    return item_dict


ModelType = TypeVar('ModelType', bound=Base)

class CRUDBase(Generic[ModelType]):

    def __init__(self, model: Type[ModelType]):
        self.model = model


    async def insert(
            self,
            data: DeclarativeBase | dict[str, Any] | list[dict[str, Any] | DeclarativeBase],
            session: AsyncSession,
            ignore_duplicates: bool = False,
            update_duplicates_keys: list[str] | None = None
    ):
        items = data if isinstance(data, list) else [data]
        if not items:
            return

        formatted_data = []
        for item in items:
            item_dict = get_state_dict(item)
            formatted_data.append(item_dict)

        stmt = mysql_insert(self.model).values(formatted_data)

        if ignore_duplicates:
            stmt = stmt.prefix_with('IGNORE')
        elif update_duplicates_keys:
            update_keys = {key: getattr(stmt.inserted, key) for key in update_duplicates_keys}
            stmt = stmt.on_duplicate_key_update(**update_keys)

        await session.execute(stmt)
        await session.flush()


    async def query(
            self,
            session: AsyncSession,
            condition: list | None = None,
            option: list | None = None,
    ):
        stmt = select(self.model)
        if condition:
            stmt = stmt.where(*condition)

        if option:
            stmt = stmt.options(*option)

        return (await session.scalars(stmt)).one_or_none()


    async def count(
            self,
            session: AsyncSession,
            condition: list | None = None,
            option: list | None = None,

    ) -> int:
        stmt = select(func.count()).select_from(self.model)
        if condition:
            stmt = stmt.where(*condition)

        if option:
            stmt = stmt.options(*option)

        return await session.scalar(stmt) or 0


    async def list(
            self,
            session: AsyncSession,
            condition: list | None = None,
            option: list | None = None,
    ):
        stmt = select(self.model)
        if condition:
            stmt = stmt.where(*condition)

        if option:
            stmt = stmt.options(*option)

        return (await session.scalars(stmt)).all()


    async def delete(
            self,
            session: AsyncSession,
            condition: list | None = None,
    ):
        stmt = delete(self.model)
        if condition:
            stmt = stmt.where(*condition)

        await session.execute(stmt)
        await session.flush()


    async def update(
            self,
            data: dict[str, Any] | DeclarativeBase,
            session: AsyncSession,
            condition: list | None = None
    ):
        stmt = update(self.model).values(**get_state_dict(data))
        if condition:
            stmt = stmt.where(*condition)

        await session.execute(stmt)
        await session.flush()


    async def bulk_update(
            self,
            data: list[dict[str, Any] | DeclarativeBase],
            session: AsyncSession
    ):
        if not data:
            return

        formatted_data = []
        for item in data:
            formatted_data.append(get_state_dict(item))

        stmt = update(self.model)
        await session.execute(stmt, formatted_data)
        await session.flush()


SemesterMixinModelType = TypeVar('SemesterMixinModelType', bound=SemesterMixin)


class CRUDSemesterMixin(CRUDBase[SemesterMixinModelType]):

    async def insert_by_semester(
            self,
            semester_id: ULID,
            data: DeclarativeBase | dict[str, Any] | list[dict[str, Any] | DeclarativeBase],
            session: AsyncSession,
            ignore_duplicates: bool = False,
            update_duplicate_keys: list[str] | None = None
    ):
        items = data if isinstance(data, list) else [data]
        if not items:
            return

        formatted_semester_id = str(semester_id)

        for item in items:
            if isinstance(item, dict):
                item["semester_id"] = formatted_semester_id
            else:
                setattr(item, "semester_id", formatted_semester_id)

        await super().insert(
            data=items,
            session=session,
            ignore_duplicates=ignore_duplicates,
            update_duplicates_keys=update_duplicate_keys
        )

    async def query_by_semester(
            self, semester_id: ULID,
            session: AsyncSession,
            condition: list | None = None,
            option: list | None = None
    ):
        conditions = list(condition) if condition else []
        conditions.append(self.model.semester_id == str(semester_id))
        return await super().query(session, condition=conditions, option=option)

    async def count_by_semester(
            self,
            semester_id: ULID,
            session: AsyncSession,
            condition: list | None = None,
            option: list | None = None
    ) -> int:
        conditions = list(condition) if condition else []
        conditions.append(self.model.semester_id == str(semester_id))
        return await super().count(session, condition=conditions, option=option)

    async def list_by_semester(
            self,
            semester_id: ULID,
            session: AsyncSession,
            condition: list | None = None,
            option: list | None = None
    ):
        conditions = list(condition) if condition else []
        conditions.append(self.model.semester_id == str(semester_id))
        return await super().list(session, condition=conditions, option=option)

    async def delete_by_semester(
            self,
            semester_id: ULID,
            session: AsyncSession,
            condition: list | None = None,
    ):
        conditions = list(condition) if condition else []
        conditions.append(self.model.semester_id == str(semester_id))
        return await super().delete(session, condition=conditions)
