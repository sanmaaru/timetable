from inspect import iscoroutine, isawaitable

import structlog
from fastapi.params import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.exceptions import AuthorizationError
from app.auth.model import User
from app.core.database import conn
from app.core.dependencies import get_current_user
from app.sync.model import SyncStatus
from app.sync.schemas import VersionResponse

logger = structlog.get_logger()
def get_status_dependency(resource: str):
    column_name=f'{resource}_version'

    async def get_version(
            user: User = Depends(get_current_user),
            session: AsyncSession = Depends(conn)
    ) -> VersionResponse:
        stmt = select(SyncStatus).where(SyncStatus.user_id == user.user_id)
        sync_status = (await session.execute(stmt)).scalars().one_or_none()

        if not sync_status:
            raise AuthorizationError('Unknown user')

        current_version = getattr(sync_status, column_name)

        return VersionResponse(version=current_version)

    return get_version