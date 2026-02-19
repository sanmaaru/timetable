from sqlalchemy import Connection, update, event, select
from sqlalchemy.orm import Mapper

from app.core.database import generate_ulid
from app.sync.model import SyncStatus
from app.theme.model import Theme, ColorScheme


def update_theme_version(mapper: Mapper, connection: Connection, target: Theme):
    user_id = target.owner_id
    new_version = generate_ulid()

    stmt = update(SyncStatus).where(SyncStatus.user_id == user_id).values(theme_version=new_version)

    connection.execute(stmt)

def update_color_scheme_version(mapper: Mapper, connection: Connection, target: ColorScheme):
    theme_id = target.theme_id
    new_version = generate_ulid()

    user_id = connection.execute(
        select(Theme.owner_id).where(Theme.theme_id == theme_id)
    ).scalars().first()

    if user_id:
        stmt = update(SyncStatus).where(SyncStatus.user_id == user_id).values(theme_version=new_version)
        connection.execute(stmt)


status = ['after_insert', 'after_update', 'after_delete']
for s in status:
    event.listen(Theme, s, update_theme_version)
    event.listen(ColorScheme, s, update_color_scheme_version)