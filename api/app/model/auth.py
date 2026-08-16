from datetime import datetime

import ulid
from sqlalchemy import String, ForeignKey, SmallInteger, Integer, DateTime, UniqueConstraint, Boolean, CHAR, \
    CheckConstraint, func
from sqlalchemy.orm import relationship, Mapped, mapped_column

from app.core.config import Configs, configs
from app.core.database import Base, ULID, generate_ulid, IdentityId
from app.model.timetable import SemesterMixin
from app.util.common import get_grade, generate_token


class User(Base):
    __tablename__ = 'users'
    __allow_unmapped__ = True

    user_id: Mapped[ulid.ULID] = mapped_column(ULID(), primary_key=True, default=generate_ulid)
    username: Mapped[str] = mapped_column(String(20), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    selected_theme_id: Mapped[ulid.ULID] = mapped_column(ULID(), ForeignKey('themes.theme_id', ondelete='RESTRICT'), nullable=True)
    identity_id: Mapped[str] = mapped_column(IdentityId(), nullable=False, unique=True)

    refresh_tokens = relationship('RefreshToken', back_populates='owner', cascade='all, delete-orphan')
    owning_themes = relationship('Theme', back_populates='owner', cascade='all, delete-orphan',
                                 foreign_keys='[Theme.owner_id]')
    selected_theme = relationship('Theme', back_populates='selectors', foreign_keys=[selected_theme_id], post_update=True)
    sync_status = relationship("SyncStatus", back_populates="user", cascade="all, delete-orphan")

    # Attribute for injected user info
    user_info: 'UserInfo | None' = None

    def __repr__(self):
        return (f'<User(user_id={self.user_id}, identity_id={self.identity_id}, username={self.username}, ' +
                f'email={self.email}, selected_theme_id={self.selected_theme_id})>')


class UserInfo(Base, SemesterMixin):
    __tablename__ = 'user_infos'

    user_info_id: Mapped[ulid.ULID] = mapped_column(ULID(), primary_key=True, default=generate_ulid)

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[int] = mapped_column(Integer, nullable=False)
    clazz: Mapped[int] = mapped_column(SmallInteger, nullable=True)
    number: Mapped[int] = mapped_column(SmallInteger, nullable=True)
    generation: Mapped[int] = mapped_column(SmallInteger, nullable=True)
    credit: Mapped[int] = mapped_column(Integer, nullable=True)
    identity_id: Mapped[str] = mapped_column(IdentityId(), nullable=True)

    taught_lectures = relationship('Lecture', back_populates='teacher_info')
    enrollments = relationship('Enrollment', back_populates='user_info', cascade='all, delete-orphan')
    lectures = relationship('Lecture', uselist=True, secondary='enrollments', back_populates='classmates')

    @property
    def grade(self) -> int:
        return get_grade(self.generation)

    def __repr__(self):
        return (
            f'<UserInfo(user_info_id={self.user_info_id}, identity_id={self.identity_id}, role={self.role}, ' +
            f'name={self.name}, generation={self.generation}, clazz={self.clazz}, number={self.number}, credit={self.credit})>'
        )

    __table_args__ = (
        UniqueConstraint('identity_id', 'semester_id', name='unique_user_info_semester'),
    )


class RefreshToken(Base):
    __tablename__ = 'refresh_tokens'

    token_id: Mapped[ulid.ULID] = mapped_column(ULID(), primary_key=True, default=generate_ulid)
    issued_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    expired_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    owner_id: Mapped[ulid.ULID] = mapped_column(ULID(), ForeignKey('users.user_id'), nullable=False)

    owner = relationship('User', back_populates='refresh_tokens')

    def __repr__(self) -> str:
        return (
            f'<RefreshToken(token_id={self.token_id}, issued_at={self.issued_at}, expired_at{self.expired_at}' +
            f'owner_id={self.owner_id})>'
        )


class IdentifyToken(Base):
    __tablename__ = 'identify_tokens'

    token_id: Mapped[str] = mapped_column(CHAR(configs.ID_TOKEN_LENGTH), primary_key=True, default=generate_token)
    identity_id: Mapped[str] = mapped_column(IdentityId(), nullable=False, unique=True)
    expired: Mapped[bool] = mapped_column(Boolean(), default=False)

    __table_args__ = (
        CheckConstraint(func.length(token_id) == configs.ID_TOKEN_LENGTH, name='check_token_length'),
    )

    def __repr__(self) -> str:
        return (
            f'<IdentityId(token_id={self.token_id}, identity_id={self.identity_id}, expired={self.expired})>'
        )