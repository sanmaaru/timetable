import ulid
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base, ULID, generate_ulid


class SyncStatus(Base):

    __tablename__ = 'sync_statuses'

    user_id: Mapped[ulid.ULID] = mapped_column(ULID(), ForeignKey('users.user_id'), primary_key=True)
    timetable_version: Mapped[ulid.ULID] = mapped_column(ULID(), nullable=False, default=generate_ulid)
    theme_version: Mapped[ulid.ULID] = mapped_column(ULID(), nullable=False, default=generate_ulid)

    user = relationship("User", back_populates="sync_status")