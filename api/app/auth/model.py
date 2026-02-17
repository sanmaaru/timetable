from datetime import datetime

import ulid
from sqlalchemy import String, ForeignKey, SmallInteger, Integer, DateTime
from sqlalchemy.orm import relationship, Mapped, mapped_column, query_expression

from app.core.database import Base, ULID, generate_ulid
from app.util.common import get_grade, generate_token


class User(Base):
    __tablename__ = 'users'

    user_id: Mapped[ulid.ULID] = mapped_column(ULID(), primary_key=True, default=generate_ulid)
    username: Mapped[str] = mapped_column(String(20), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    user_info_id: Mapped[ulid.ULID] = mapped_column(ULID(), ForeignKey('user_infos.user_info_id'), nullable=False, unique=True)
    selected_theme_id: Mapped[ulid.ULID] = mapped_column(ULID(), ForeignKey('themes.theme_id', ondelete='RESTRICT'), nullable=True)

    user_info = relationship('UserInfo', uselist=False, back_populates='user')
    refresh_tokens = relationship('RefreshToken', back_populates='owner', cascade='all, delete-orphan')
    owning_themes = relationship('Theme', back_populates='owner', cascade='all, delete-orphan',
                                 foreign_keys='[Theme.owner_id]')
    selected_theme = relationship('Theme', back_populates='selectors', foreign_keys=[selected_theme_id], post_update=True)

    def __repr__(self):
        return (f'<User(user_id={self.user_id}, username={self.username}, '
                f'email={self.email}, user_info_id={self.user_info_id}, selected_theme_id={self.selected_theme_id})>')


class UserInfo(Base):
    __tablename__ = 'user_infos'

    user_info_id: Mapped[ulid.ULID] = mapped_column(ULID(), primary_key=True, default=generate_ulid)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[int] = mapped_column(Integer, nullable=False)
    clazz: Mapped[int] = mapped_column(SmallInteger, nullable=True)
    number: Mapped[int] = mapped_column(SmallInteger, nullable=True)
    generation: Mapped[int] = mapped_column(SmallInteger, nullable=True)
    credit: Mapped[int] = mapped_column(Integer, nullable=True)

    taught_lectures = relationship('Lecture', back_populates='teacher_info')
    enrollments = relationship('Enrollment', back_populates='user_info', cascade='all, delete-orphan')
    classes = relationship('Class', secondary='enrollments', back_populates='classmates')

    user = relationship('User', uselist=False, back_populates='user_info')

    @property
    def grade(self):
        return get_grade(self.generation)


class RefreshToken(Base):
    __tablename__ = 'refresh_tokens'

    token_id: Mapped[ulid.ULID] = mapped_column(ULID(), primary_key=True, default=generate_ulid)
    issued_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    expired_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    owner_id: Mapped[ulid.ULID] = mapped_column(ULID(), ForeignKey('users.user_id'), nullable=False)

    owner = relationship('User', back_populates='refresh_tokens')


class IdentifyToken(Base):
    __tablename__ = 'identify_tokens'

    token_id: Mapped[str] = mapped_column(String(8), primary_key=True, default=generate_token)
    user_info_id: Mapped[ulid.ULID] = mapped_column(ULID(), ForeignKey('user_infos.user_info_id'), nullable=False, unique=True)

    user_info = relationship('UserInfo', uselist=False)