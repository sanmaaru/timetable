from sqlalchemy import Column, String, ForeignKey, SmallInteger, Integer, Float
from sqlalchemy.orm import relationship

from database import Base, ULID
from util import get_grade


class User(Base):
    __tablename__ = 'users'

    user_id = Column(String(36), primary_key=True)
    username = Column(String(20), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)
    user_info_id = Column(String(36), ForeignKey('users_info.user_info_id'), nullable=False, unique=True)
    selected_theme_id = Column(ULID(), ForeignKey('themes.theme_id', ondelete='RESTRICT'))

    user_info = relationship('UserInfo', uselist=False, back_populates='user')
    refresh_tokens = relationship('RefreshToken', back_populates='owner', cascade='all, delete-orphan')
    owning_themes = relationship('Theme', back_populates='owner', cascade='all, delete-orphan',
                                 foreign_keys='[Theme.owner_id]')
    selected_theme = relationship('Theme', back_populates='selectors', foreign_keys=[selected_theme_id], post_update=True)

    def __repr__(self):
        return 'user { user_id: {' + str(self.user_id) + '}, username: {' + str(self.username) + '}, email: {' + str(
            self.email) + '} }'


class UserInfo(Base):
    __tablename__ = 'users_info'

    user_info_id = Column(String(36), primary_key=True)
    name = Column(String(255), nullable=False)
    role = Column(Integer, nullable=False)
    clazz = Column(SmallInteger, nullable=True)
    number = Column(SmallInteger, nullable=True)
    generation = Column(SmallInteger, nullable=True)
    credit = Column(Integer, nullable=True)

    taught_lectures = relationship('Lecture', back_populates='teacher_info')
    enrollments = relationship('Enrollment', back_populates='user_info', cascade='all, delete-orphan')
    classes = relationship('Class', secondary='enrollments', back_populates='students_info')

    user = relationship('User', uselist=False, back_populates='user_info')

    @property
    def grade(self):
        return get_grade(self.generation)


class RefreshToken(Base):
    __tablename__ = 'refresh_tokens'

    token_id = Column(String(36), primary_key=True)
    issuer = Column(String(255), nullable=False)
    issued_at = Column(Float(), nullable=False)
    expired_at = Column(Float(), nullable=False)
    jwt_signature = Column(String(255), nullable=False)
    owner_id = Column(String(36), ForeignKey('users.user_id'), nullable=False)

    owner = relationship('User', back_populates='refresh_tokens')


class IdentifyToken(Base):
    __tablename__ = 'identify_tokens'

    token_id = Column(String(8), primary_key=True)
    user_info_id = Column(String(36), ForeignKey('users_info.user_info_id'), nullable=False, unique=True)

    user_info = relationship('UserInfo', uselist=False)
